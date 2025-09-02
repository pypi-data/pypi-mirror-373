"""This module provides receivers task's signals."""
import time

from celery import signals
from celery import states as task_states
from celery.app.task import Task
from celery.exceptions import Reject, Retry

from celery_control import metrics
from celery_control.conf import state


def connect() -> None:  # noqa: WPS213
    """Connect task signals."""
    signals.task_success.connect(_receive_task_success)
    signals.task_failure.connect(_receive_task_failure)
    signals.task_retry.connect(_receive_task_retry)
    signals.task_internal_error.connect(_receive_task_internal_error)
    signals.task_rejected.connect(_receive_task_rejected)
    signals.task_unknown.connect(_receive_task_unknown)
    signals.task_revoked.connect(_receive_task_revoked)
    signals.task_prerun.connect(_receive_task_prerun)
    signals.task_postrun.connect(_receive_task_postrun)


# noinspection PyUnusedLocal
def _receive_task_success(sender: Task, **kwargs) -> None:                           # type: ignore[no-untyped-def]
    """
    Receive task_success signal.

    Increment task_succeeded_total counter.

    Args:
        sender: Task.
        kwargs: Must be specified to pass celery's checks.
    """
    metrics.task_succeeded_total.labels(worker=state.worker_name, task=sender.name).inc()


# noinspection PyUnusedLocal
def _receive_task_failure(sender: Task, exception: Exception, **kwargs) -> None:     # type: ignore[no-untyped-def]
    """
    Receive task_failure signal.

    Increment task_failed_total counter.

    Args:
        sender: Task.
        exception: Exception.
        kwargs: Must be specified to pass celery's checks.
    """
    exception_type_name = type(exception).__name__
    metrics.task_failed_total.labels(
        worker=state.worker_name,
        task=sender.name,
        exception=exception_type_name,
    ).inc()


# noinspection PyUnusedLocal
def _receive_task_retry(sender: Task, **kwargs) -> None:                             # type: ignore[no-untyped-def]
    """
    Receive task_retry signal.

    Increment task_retried_total counter.

    Args:
        sender: Task.
        kwargs: Must be specified to pass celery's checks.
    """
    exception_type_name = 'undefined'
    reason: Retry | None = kwargs.get('reason')
    if reason and reason.exc:
        exception_type_name = type(reason.exc).__name__

    metrics.task_retried_total.labels(
        worker=state.worker_name,
        task=sender.name,
        exception=exception_type_name,
    ).inc()


# noinspection PyUnusedLocal
def _receive_task_internal_error(sender: Task, exception: Exception, **kwargs) -> None:  # type: ignore[no-untyped-def]
    """
    Receive task_internal_error signal.

    Increment task_internal_error_total counter.

    Args:
        sender: Task.
        exception: Exception.
        kwargs: Must be specified to pass celery's checks.
    """
    exception_type_name = type(exception).__name__

    metrics.task_internal_error_total.labels(
        worker=state.worker_name,
        task=sender.name,
        exception=exception_type_name,
    ).inc()


# noinspection PyUnusedLocal
def _receive_task_rejected(**kwargs) -> None:                                        # type: ignore[no-untyped-def]
    """
    Receive task_rejected signal.

    Increment message_rejected_total counter.

    Args:
        kwargs: Must be specified to pass celery's checks.
    """
    metrics.message_rejected_total.labels(worker=state.worker_name).inc()


# noinspection PyUnusedLocal
def _receive_task_unknown(**kwargs) -> None:                                         # type: ignore[no-untyped-def]
    """
    Receive task_unknown signal.

    Increment task_unknown_total counter.

    Args:
        kwargs: Must be specified to pass celery's checks.
    """
    metrics.task_unknown_total.labels(worker=state.worker_name).inc()


# noinspection PyUnusedLocal
def _receive_task_revoked(                                                           # type: ignore[no-untyped-def]
    sender: Task,
    terminated: bool,
    expired: bool,
    **kwargs,
) -> None:
    """
    Receive task_revoked signal.

    Increment task_revoked_total counter.

    Args:
        sender: Task.
        terminated: Task was terminated.
        expired: Task was expired.
        kwargs: Must be specified to pass celery's checks.
    """
    metrics.task_revoked_total.labels(
        worker=state.worker_name,
        task=sender.name,
        terminated=str(terminated).lower(),
        expired=str(expired).lower(),
    ).inc()


# noinspection PyUnusedLocal
def _receive_task_prerun(sender: Task, **kwargs) -> None:                            # type: ignore[no-untyped-def]
    """
    Receive task_prerun signal.

    Set celery_control_time_start to sender.request.

    Args:
        sender: Task.
        kwargs: Must be specified to pass celery's checks.
    """
    metrics.task_accepted_total.labels(worker=state.worker_name, task=sender.name).inc()

    setattr(sender.request, 'celery_control_task_time_start', time.monotonic())     # noqa: B010


# noinspection PyUnusedLocal
def _receive_task_postrun(sender: Task, **kwargs) -> None:                           # type: ignore[no-untyped-def]
    """
    Receive task_postrun signal.

    Get celery_control_task_time_start from sender.request and observe task_runtime_seconds Histogram.

    If task_state is REJECTED, increment task_rejected_total counter.

    Args:
        sender: Task.
        kwargs: Must be specified to pass celery's checks.
    """
    time_start = getattr(sender.request, 'celery_control_task_time_start')          # noqa: B009
    task_runtime_seconds = time.monotonic() - time_start

    metrics.task_runtime_seconds.labels(worker=state.worker_name, task=sender.name).observe(task_runtime_seconds)

    task_state, task_retval = kwargs.get('state'), kwargs.get('retval')

    if task_state == task_states.REJECTED:
        requeue = 'unknown'
        if isinstance(task_retval, Reject):
            requeue = str(task_retval.requeue).lower()

        metrics.task_rejected_total.labels(
            worker=state.worker_name,
            task=sender.name,
            requeue=requeue,
        ).inc()
