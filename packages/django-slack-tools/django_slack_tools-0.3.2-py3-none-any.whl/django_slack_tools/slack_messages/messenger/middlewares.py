# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from django_slack_tools.messenger.shortcuts import BaseMiddleware, MessageHeader, MessageRequest
from django_slack_tools.slack_messages.models import SlackMessage, SlackMessageRecipient, SlackMessagingPolicy

if TYPE_CHECKING:
    from django_slack_tools.messenger.shortcuts import MessageResponse, Messenger

logger = logging.getLogger(__name__)


class DjangoDatabasePersister(BaseMiddleware):
    """Persist message history to database. If request is `None`, will do nothing."""

    def __init__(self, *, slack_app: App | None = None, get_permalink: bool = False) -> None:
        """Initialize the middleware.

        Args:
            slack_app: Slack app instance to use for certain tasks, such as getting permalinks.
            get_permalink: If `True`, will try to get the permalink of the message.
        """
        if get_permalink and not isinstance(slack_app, App):
            msg = "`slack_app` must be an instance of `App` if `get_permalink` is set `True`."
            raise ValueError(msg)

        self.slack_app = slack_app
        self.get_permalink = get_permalink

    def process_response(self, response: MessageResponse) -> MessageResponse | None:  # noqa: D102
        request = response.request
        if request is None:
            logger.warning("No request found in response, skipping persister.")
            return response

        logger.debug("Getting permalink for message: %s", response)
        if self.get_permalink:  # noqa: SIM108
            permalink = self._get_permalink(channel=request.channel, ts=response.ts)
        else:
            permalink = ""

        logger.debug("Persisting message history to database: %s", response)
        try:
            history = SlackMessage(
                id=request.id_,
                channel=request.channel,
                header=request.header.model_dump(),
                body=request.body.model_dump() if request.body else {},
                ok=response.ok,
                permalink=permalink,
                ts=response.ts,
                parent_ts=response.parent_ts or "",
                request=request.model_dump(),
                response=response.model_dump(exclude={"request"}),
                exception=response.error or "",
            )
            history.save()
        except Exception:
            logger.exception("Error while saving message history: %s", response)

        return response

    def _get_permalink(self, *, channel: str, ts: str | None) -> str:
        """Get permalink of the message. It returns empty string on error."""
        if not self.slack_app:
            logger.warning("Slack app not provided, cannot get permalink.")
            return ""

        if not ts:
            logger.warning("No message ts provided, cannot get permalink.")
            return ""

        try:
            response = self.slack_app.client.chat_getPermalink(channel=channel, message_ts=ts)
            return response.get("permalink", default="")
        except SlackApiError as err:
            logger.debug("Error while getting permalink: %s", exc_info=err)
            return ""


OnPolicyNotExists = Literal["create", "default", "error"]


class DjangoDatabasePolicyHandler(BaseMiddleware):
    """Middleware to handle Slack messaging policies stored in the database.

    Be cautious when using this middleware because it includes functionality to distribute messages to multiple recipients,
    which could lead to unwanted infinite loop or recursion if used improperly.

    This middleware contains a secondary protection against infinite loops by injecting a context key to the message context.
    If the key is found in the context, the middleware will stop the message from being sent. So be careful when modifying the context.
    """  # noqa: E501

    _RECURSION_DETECTION_CONTEXT_KEY = "__final__"
    """Recursion detection key injected to message context for fanned-out messages to provide secondary protection against infinite loops."""  # noqa: E501

    def __init__(
        self,
        *,
        messenger: Messenger | str,
        on_policy_not_exists: OnPolicyNotExists = "error",
    ) -> None:
        """Initialize the middleware.

        This middleware will load the policy from the database and send the message to all recipients.

        Args:
            messenger: Messenger instance or name to use for sending messages.
                The messenger instance should be different from the one used in the policy handler,
                because this middleware cannot properly handle fanned-out messages modified by this middleware.
                Also, there are chances of infinite loops if the same messenger is used.
            on_policy_not_exists: Action to take when policy is not found.
        """
        if on_policy_not_exists not in ("create", "default", "error"):
            msg = f'Unknown value for `on_policy_not_exists`: "{on_policy_not_exists}"'
            raise ValueError(msg)

        self._messenger = messenger
        self.on_policy_not_exists = on_policy_not_exists

    # * It's not desirable to put import in the method,
    # * but it's the only way to avoid circular imports for now (what's the fix?)
    @property
    def messenger(self) -> Messenger:
        """Get the messenger instance. If it's a string, will get the messenger from the app settings."""
        if isinstance(self._messenger, str):
            from django_slack_tools.app_settings import get_messenger  # noqa: PLC0415

            self._messenger = get_messenger(self._messenger)

        return self._messenger

    def process_request(self, request: MessageRequest) -> MessageRequest | None:  # noqa: D102
        # TODO(lasuillard): Hacky way to stop the request, need to find a better way
        #                   Some extra field (request.meta) could be added to share control context
        if request.context.get(self._RECURSION_DETECTION_CONTEXT_KEY, False):
            return request

        code = request.channel
        policy = self._get_policy(code=code)
        if not policy.enabled:
            logger.debug("Policy %s is disabled, skipping further messaging", policy)
            return None

        requests: list[MessageRequest] = []
        for recipient in policy.recipients.all():
            default_context = self._get_default_context(recipient)
            context = {
                **default_context,
                **request.context,
                self._RECURSION_DETECTION_CONTEXT_KEY: True,
            }
            header = MessageHeader.model_validate(
                {
                    **policy.header_defaults,
                    **request.header.model_dump(),
                },
            )
            req = MessageRequest(channel=recipient.channel, template_key=policy.code, context=context, header=header)
            requests.append(req)

        # TODO(lasuillard): How to provide users the access the newly created messages?
        #                   currently, it's possible with persisters but it would require some additional work
        # TODO(lasuillard): Can `sys.setrecursionlimit` be used to prevent spamming if recursion occurs?
        for req in requests:
            self.messenger.send_request(req)

        # Stop current request
        return None

    def _get_policy(self, *, code: str) -> SlackMessagingPolicy:
        """Get the policy for the given code."""
        try:
            policy = SlackMessagingPolicy.objects.get(code=code)
        except SlackMessagingPolicy.DoesNotExist:
            if self.on_policy_not_exists == "create":
                logger.warning("No policy found for template key, creating one: %s", code)
                policy = self._create_policy(code=code)
            elif self.on_policy_not_exists == "default":
                policy = SlackMessagingPolicy.objects.get(code="DEFAULT")
            elif self.on_policy_not_exists == "error":
                raise
            else:
                msg = f'Unknown value for `on_policy_not_exists`: "{self.on_policy_not_exists}"'
                raise ValueError(msg) from None

        return policy

    def _create_policy(self, *, code: str) -> SlackMessagingPolicy:
        """Create a policy with the given code.

        Policy created is disabled by default, thus no message will be sent.
        To modify the default policy creation behavior, simply override this method.
        """
        policy = SlackMessagingPolicy.objects.create(
            code=code,
            enabled=False,
            template_type=SlackMessagingPolicy.TemplateType.UNKNOWN,
        )
        default_recipients = SlackMessageRecipient.objects.filter(alias="DEFAULT")
        policy.recipients.set(default_recipients)
        return policy

    def _get_default_context(self, recipient: SlackMessageRecipient) -> dict:
        """Create default context for the recipient."""
        mentions = [mention.mention for mention in recipient.mentions.all()]
        return {
            "mentions": mentions,
        }
