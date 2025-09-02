"""This module provides publish signals receivers."""
from celery import signals

from celery_control import metrics


def connect() -> None:
    """Connect publish signals."""
    signals.after_task_publish.connect(_receive_after_task_publish)


# noinspection PyUnusedLocal
def _receive_after_task_publish(sender: str, **kwargs) -> None:         # type: ignore[no-untyped-def]
    """
    Receive after_task_publish signal.

    Args:
        sender: The task name.
        kwargs: Other arguments. Must be specified to pass celery's checks.
    """
    metrics.task_published_total.labels(task=sender).inc()
