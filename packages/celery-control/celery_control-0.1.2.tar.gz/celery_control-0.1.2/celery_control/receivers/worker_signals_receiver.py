"""This module provides receivers worker's signals."""
import logging
import os

from celery import signals
from celery.apps.worker import Worker
from celery.worker.consumer import Consumer

from celery_control import multiprocess, observable, tracker
from celery_control.conf import settings, state
from celery_control.server.wsgi import start_wsgi_server

logger = logging.getLogger('celery')

# noinspection HttpUrlsUsage
LOG_HTTP_SERVER_STARTING = 'celery control: staring HTTP server http://%s:%s'
LOG_HTTP_SERVER_STARTED_SUCCESSFULLY = 'celery control: HTTP server started successfully'
LOG_HTTP_SERVER_FAILED = "celery control: can't start HTTP server. %s"
LOG_TRACKER_STARTING = 'celery control: staring tracker in daemon thread'
LOG_MULTIPROCESS_MODE = 'celery control: multiprocess mode %s'
LOG_MULTIPROCESS_MODE_WITHOUT_LOCK = "celery control: multiprocess mode enabled, but can't get worker_id_lock"
LOG_MULTIPROCESS_PATH_FOR_METRICS = 'celery control: multiprocess path for metrics %s'
LOG_MULTIPROCESS_PATH_FOR_LOCKS = 'celery control: multiprocess path for locks   %s'
LOG_PROCESS_IDENTIFIER_USE = 'celery control: use process_identifier (%s)'
LOG_PROCESS_IDENTIFIER_SET = 'celery control: set process_identifier (%s)'
LOG_PROCESS_IDENTIFIER_MARK_AS_DEAD = 'celery control: mark process as dead (%s)'
LOG_REGISTERED_OBSERVABLE_METRIC = 'celery control: registered observable metric %s'


def connect() -> None:
    """Connect worker signals."""
    signals.worker_init.connect(_receive_worker_init)
    signals.worker_ready.connect(_receive_worker_ready)
    signals.worker_shutdown.connect(receive_worker_shutdown)
    signals.worker_process_init.connect(_receive_worker_process_init)
    signals.worker_process_shutdown.connect(_receive_worker_process_shutdown)


# noinspection PyUnusedLocal
def _receive_worker_init(sender: Worker, **kwargs) -> None:                          # type: ignore[no-untyped-def]
    """
    Receive worker_init signal.

    If multiprocess mode is enabled, process_identifier becomes the worker's hostname.
    Then sets process_identifier for the prometheus_clint's MultiProcessValue.

    Args:
        sender: Celery worker.
        kwargs: Must be specified to pass celery's checks.
    """
    state.worker_id = sender.hostname
    state.worker_id_lock = None
    state.worker_name = sender.hostname
    state.worker_concurrency = sender.concurrency
    state.worker_process_identifier = state.worker_name

    if settings.multiprocess_enabled:
        multiprocess.set_process_identifier(state.worker_process_identifier)


# noinspection PyUnusedLocal
def _receive_worker_ready(sender: Consumer, **kwargs) -> None:       # type: ignore[no-untyped-def] # noqa: WPS213
    """
    Receive worker_ready signal.

    Try to start http server. If fails, start tracker in daemon thread.

    Args:
        sender: Celery consumer.
        kwargs: Must be specified to pass celery's checks.
    """
    state.consumer = sender

    logger.info(LOG_MULTIPROCESS_MODE, 'enabled' if settings.multiprocess_enabled else 'disabled')

    if settings.multiprocess_enabled:
        logger.info(LOG_MULTIPROCESS_PATH_FOR_METRICS, os.path.abspath(settings.multiprocess_dir or ''))
        logger.info(LOG_MULTIPROCESS_PATH_FOR_LOCKS, os.path.abspath(settings.multiprocess_dir_locks or ''))
        logger.info(LOG_PROCESS_IDENTIFIER_USE, state.worker_process_identifier)
        _warn_registered_observable_metrics()

    need_track_in_daemon = False

    logger.info(LOG_HTTP_SERVER_STARTING, settings.server_host, settings.server_port)
    try:
        start_wsgi_server()
    except OSError as exc:
        logger.warning(LOG_HTTP_SERVER_FAILED, exc.strerror)
        need_track_in_daemon = True
    except Exception as exc:
        logger.error(LOG_HTTP_SERVER_FAILED, str(exc))
    else:
        logger.info(LOG_HTTP_SERVER_STARTED_SUCCESSFULLY)

    if need_track_in_daemon and settings.multiprocess_enabled:
        logger.info(LOG_TRACKER_STARTING)
        tracker.start_daemon()


# noinspection PyUnusedLocal
def receive_worker_shutdown(**kwargs) -> None:                                      # type: ignore[no-untyped-def]
    """
    Receive worker_shutdown signal.

    If multiprocess mode is enabled, the corresponding process_identifier will be marked as dead.

    Args:
        kwargs: Must be specified to pass celery's checks.
    """
    if settings.multiprocess_enabled:
        logger.info(LOG_PROCESS_IDENTIFIER_MARK_AS_DEAD, state.worker_process_identifier)
        multiprocess.mark_process_identifier_as_dead(state.worker_process_identifier)


# noinspection PyUnusedLocal
def _receive_worker_process_init(**kwargs) -> None:                                  # type: ignore[no-untyped-def]
    """
    Receive worker_process_init signal.

    If multiprocess mode is enabled, it will try to acquire a lock file.

    When lock is success, worker_id will be a number between 1 and the worker's concurrency.
    It stores a reference to the lock file in the state,
    because the lock will be released automatically after delete all references.

    When lock is fail, worker_id will be a pid. It's default behavior for multiprocess mode.

    Next makes process_identifier and sets for the prometheus_clint's MultiProcessValue.

    Args:
        kwargs: Must be specified to pass celery's checks.
    """
    if settings.multiprocess_enabled:
        worker_id, worker_id_lock = multiprocess.get_worker_id(
            concurrency=state.worker_concurrency,
            name=state.worker_name,
        )

        state.worker_id = worker_id
        state.worker_id_lock = worker_id_lock
        state.worker_process_identifier = multiprocess.make_process_identifier(
            worker_name=state.worker_name,
            worker_id=state.worker_id,
            has_lock=worker_id_lock is not None,
        )
        if not worker_id_lock:
            logger.warning(LOG_MULTIPROCESS_MODE_WITHOUT_LOCK)

        logger.info(LOG_PROCESS_IDENTIFIER_SET, state.worker_process_identifier)
        multiprocess.set_process_identifier(state.worker_process_identifier)


# noinspection PyUnusedLocal
def _receive_worker_process_shutdown(**kwargs) -> None:                              # type: ignore[no-untyped-def]
    """
    Receive worker_process signal.

    If multiprocess mode is enabled, the corresponding process_identifier will be marked as dead.

    Args:
        kwargs: Must be specified to pass celery's checks.
    """
    if settings.multiprocess_enabled:
        logger.info(LOG_PROCESS_IDENTIFIER_MARK_AS_DEAD, state.worker_process_identifier)
        multiprocess.mark_process_identifier_as_dead(state.worker_process_identifier)


def _warn_registered_observable_metrics() -> None:
    try:
        observable_metrics = observable.get_observable_metric_names(settings.registry)
    except Exception:
        return

    for observable_metric_name in observable_metrics:
        logger.warning(LOG_REGISTERED_OBSERVABLE_METRIC, observable_metric_name)
