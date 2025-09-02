"""This module provides methods for configuring celery."""
import logging
import os
from typing import Callable

from prometheus_client import REGISTRY, CollectorRegistry

from celery_control import metrics
from celery_control.conf import settings
from celery_control.receivers import publish_signals_receiver, task_signals_receiver, worker_signals_receiver
from celery_control.server import wsgi
from celery_control.utils.strtobool import str2bool_exc

logger = logging.getLogger('celery')

# noinspection HttpUrlsUsage
LOG_HTTP_SERVER_STARTING = 'celery control: staring HTTP server http://%s:%s'
LOG_HTTP_SERVER_STARTED_SUCCESSFULLY = 'celery control: HTTP server started successfully'
LOG_HTTP_SERVER_FAILED = "celery control: can't start HTTP server. %s"

ENV_SERVER_HOST = os.environ.get('CELERY_CONTROL_SERVER_HOST', '0.0.0.0')
ENV_SERVER_PORT = int(os.environ.get('CELERY_CONTROL_SERVER_PORT', 5555))
ENV_SERVER_DISABLE_COMPRESSION = str2bool_exc(os.environ.get('CELERY_CONTROL_SERVER_DISABLE_COMPRESSION', 'False'))
ENV_TRACKER_DAEMON_INTERVAL = int(os.environ.get('CELERY_CONTROL_TRACKER_DAEMON_INTERVAL', 15))


def setup_worker(
    registry: CollectorRegistry = REGISTRY,
    server_host: str = ENV_SERVER_HOST,
    server_port: int = ENV_SERVER_PORT,
    server_disable_compression: bool = ENV_SERVER_DISABLE_COMPRESSION,
    tracker_daemon_interval: int = ENV_TRACKER_DAEMON_INTERVAL,
    tracker_application_callback: Callable[[], None] | None = None,
    task_runtime_buckets: tuple[float, ...] | None = None,
) -> None:
    """Configure metrics for worker."""
    settings.registry = registry
    settings.server_host = server_host
    settings.server_port = server_port
    settings.server_disable_compression = server_disable_compression

    settings.tracker_enabled = True
    settings.tracker_daemon_interval = tracker_daemon_interval
    settings.tracker_application_callback = tracker_application_callback

    metrics.register_worker_metrics(registry, task_runtime_buckets=task_runtime_buckets)

    publish_signals_receiver.connect()
    task_signals_receiver.connect()
    worker_signals_receiver.connect()


def setup_publisher(
    registry: CollectorRegistry = REGISTRY,
    start_wsgi_server: bool = False,
    server_host: str = ENV_SERVER_HOST,
    server_port: int = ENV_SERVER_PORT,
    server_disable_compression: bool = ENV_SERVER_DISABLE_COMPRESSION,
    tracker_application_callback: Callable[[], None] | None = None,
) -> None:
    """Configure metrics for publisher."""
    settings.registry = registry
    settings.server_host = server_host
    settings.server_port = server_port
    settings.server_disable_compression = server_disable_compression

    settings.tracker_enabled = False
    settings.tracker_application_callback = tracker_application_callback

    metrics.register_publisher_metrics(registry)

    publish_signals_receiver.connect()

    if start_wsgi_server:
        _start_wsgi_server()


def _start_wsgi_server() -> None:
    logger.info(LOG_HTTP_SERVER_STARTING, settings.server_host, settings.server_port)
    try:
        wsgi.start_wsgi_server()
    except OSError as exc:
        logger.warning(LOG_HTTP_SERVER_FAILED, exc.strerror)
    except Exception as exc:
        logger.warning(LOG_HTTP_SERVER_FAILED, str(exc))
    else:
        logger.info(LOG_HTTP_SERVER_STARTED_SUCCESSFULLY)
