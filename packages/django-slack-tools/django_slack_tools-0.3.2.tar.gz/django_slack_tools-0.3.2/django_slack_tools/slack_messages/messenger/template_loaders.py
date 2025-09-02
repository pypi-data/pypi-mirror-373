# noqa: D100
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.template import TemplateDoesNotExist, engines

from django_slack_tools.messenger.shortcuts import BaseTemplateLoader, PythonTemplate
from django_slack_tools.slack_messages.models import SlackMessagingPolicy

from .message_templates import DjangoTemplate

if TYPE_CHECKING:
    from django.template.backends.base import BaseEngine


logger = logging.getLogger(__name__)


class DjangoTemplateLoader(BaseTemplateLoader):
    """Django filesystem-backed template loader."""

    def __init__(self, *, engine: BaseEngine | None = None) -> None:
        """Initialize template loader.

        Args:
            engine: Template engine to use. Defaults to Django engine.
        """
        self.engine = engines["django"] if engine is None else engine

    def load(self, key: str) -> DjangoTemplate | None:  # noqa: D102
        try:
            return DjangoTemplate(file=key, engine=self.engine)
        except TemplateDoesNotExist:
            logger.debug("Template not found: %s", key)
            return None


class DjangoPolicyTemplateLoader(BaseTemplateLoader):
    """Django database-backed template loader."""

    def load(self, key: str) -> PythonTemplate | DjangoTemplate | None:  # noqa: D102
        return self._get_template_from_policy(policy_or_code=key)

    def _get_template_from_policy(
        self,
        policy_or_code: SlackMessagingPolicy | str,
    ) -> PythonTemplate | DjangoTemplate | None:
        """Get template instance."""
        if isinstance(policy_or_code, str):
            try:
                policy = SlackMessagingPolicy.objects.get(code=policy_or_code)
            except SlackMessagingPolicy.DoesNotExist:
                logger.warning("Policy not found: %s", policy_or_code)
                return None
        else:
            policy = policy_or_code

        if policy.template_type == SlackMessagingPolicy.TemplateType.PYTHON:
            return PythonTemplate(policy.template)

        if policy.template_type == SlackMessagingPolicy.TemplateType.DJANGO:
            try:
                return DjangoTemplate(file=policy.template)
            except TemplateDoesNotExist:
                logger.debug("Template not found: %s", policy.template)
                return None

        if policy.template_type == SlackMessagingPolicy.TemplateType.DJANGO_INLINE:
            return DjangoTemplate(inline=policy.template)

        msg = f"Unsupported template type: {policy.template_type!r}"
        raise ValueError(msg)
