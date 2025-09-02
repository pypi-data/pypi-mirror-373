"""This module provides the methods for track some metrics."""
import logging
import threading
import time
from collections import defaultdict

from celery.worker.request import Request
from celery.worker.state import total_count
from prometheus_client import Gauge

from celery_control import metrics, snapshot
from celery_control.conf import settings, state

logger = logging.getLogger('celery')

LOG_TRACKING_METRICS = 'celery control: tracking metrics'
LOG_TRACK_ERROR = "celery control: Can't track metrics"


def start_daemon() -> None:
    """Start tracking in daemon thread."""
    thread = threading.Thread(target=_daemon)
    thread.daemon = True
    thread.start()


def track() -> None:
    """
    Track celery worker metrics.

    First, set worker_online Gauge to current time.

    Second, fill state.tasks_seen.

    Then update requests statistics for the current moment.
    """
    metrics.worker_online.labels(worker=state.worker_name).set_to_current_time()

    _fill_tasks_seen()

    requests_snapshot = snapshot.make_requests_snapshot()

    _track_requests_statistics(requests_snapshot.prefetched, metrics.task_prefetched)
    _track_requests_statistics(requests_snapshot.active, metrics.task_active)
    _track_requests_statistics(requests_snapshot.waiting, metrics.task_waiting)
    _track_requests_statistics(requests_snapshot.scheduled, metrics.task_scheduled)

    if settings.tracker_application_callback is not None:
        settings.tracker_application_callback()


def _daemon() -> None:
    while True:
        logger.debug(LOG_TRACKING_METRICS)
        try:
            track()
        except Exception:
            logger.exception(LOG_TRACK_ERROR)

        time.sleep(settings.tracker_daemon_interval)


def _track_requests_statistics(requests: set[Request], metric: Gauge) -> None:
    counter: dict[str, int] = defaultdict(int)

    for request in requests:
        counter[request.task.name] += 1

    for task, cnt in counter.items():
        metric.labels(task=task, worker=state.worker_name).set(cnt)
        state.tasks_seen.add(task)

    for task_seen in state.tasks_seen:
        if task_seen not in counter:
            metric.labels(task=task_seen, worker=state.worker_name).set(0)


def _fill_tasks_seen() -> None:
    # fill from accepted counter
    for task_accepted in total_count.keys():
        state.tasks_seen.add(task_accepted)
