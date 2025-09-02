"""Celery utils."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from . import shortcuts
from .models import SlackMessage

if TYPE_CHECKING:
    from typing import Any

logger = get_task_logger(__name__)


@shared_task
def slack_message(*args: Any, **kwargs: Any) -> str | None:
    """Celery task wrapper for `.shortcuts.slack_message`.

    Args:
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        ID of sent message if any, `None` otherwise.
    """
    response = shortcuts.slack_message(*args, **kwargs)
    return response.ts if response else None


@shared_task
def cleanup_old_messages(
    *,
    base_ts: str | None = None,
    threshold_seconds: int | None = 7 * 24 * 60 * 60,  # 7 days
) -> int:
    """Delete old messages created before given threshold.

    Args:
        threshold_seconds: Threshold seconds. Defaults to 7 days.
        base_ts: Base timestamp to calculate the threshold, in ISO format. If falsy, current timestamp will be used.

    Returns:
        Number of deleted messages.
    """
    dt = datetime.fromisoformat(base_ts) if base_ts else timezone.localtime()

    if threshold_seconds is None:
        logger.warning("Threshold seconds not provided, skipping cleanup.")
        return 0

    cleanup_threshold = dt - timedelta(seconds=threshold_seconds)
    logger.debug("Cleaning up messages older than %s.", cleanup_threshold)

    num_deleted, _ = SlackMessage.objects.filter(created__lt=cleanup_threshold).delete()
    logger.info("Deleted %d old messages.", num_deleted)

    return num_deleted
