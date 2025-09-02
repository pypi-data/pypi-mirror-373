"""This module provides WSGI app and method for starting server."""
import threading
from typing import Any, Callable, Tuple, TypeAlias
from wsgiref.simple_server import WSGIServer, make_server

from prometheus_client import CollectorRegistry
from prometheus_client.multiprocess import MultiProcessCollector

from celery_control import tracker
from celery_control.conf import settings
from celery_control.server import exposition
from celery_control.server.socket import get_best_family
from celery_control.server.types import TypeOutput
from celery_control.server.wsgiref import SilentHandler, ThreadingWSGIServer

TypeStartResponse: TypeAlias = Callable[[str, list[tuple[str, str]]], Callable[[bytes], object]]    # noqa: WPS221
TypeWSGIEnviron: TypeAlias = dict[str, Any]


def start_wsgi_server() -> Tuple[WSGIServer, threading.Thread]:                                     # noqa: WPS210
    """Start a WSGI server for prometheus metrics as a daemon thread."""
    family, host, port = get_best_family(settings.server_host, settings.server_port)

    class TmpServer(ThreadingWSGIServer):                                                           # noqa: WPS431
        """Copy of ThreadingWSGIServer to update address_family locally."""

        address_family = family

    server = make_server(
        host=host,
        port=port,
        app=app,
        server_class=TmpServer,
        handler_class=SilentHandler,
    )

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    return server, thread


def app(environ: TypeWSGIEnviron, start_response: TypeStartResponse) -> list[bytes]:
    """WSGI app for returning prometheus client metrics."""
    if environ['PATH_INFO'] == '/favicon.ico':
        status, headers, output = _output_favicon(environ)
    else:
        status, headers, output = _output_metrics(environ)

    start_response(status, headers)

    return [output]


# noinspection PyUnusedLocal
def _output_favicon(environ: TypeWSGIEnviron) -> TypeOutput:
    return '200 OK', [('', '')], b''


def _output_metrics(environ: TypeWSGIEnviron) -> TypeOutput:
    if settings.tracker_enabled:
        # Track metrics before exposition
        tracker.track()
    elif settings.tracker_application_callback is not None:
        # Track only application metrics before exposition
        settings.tracker_application_callback()

    registry = settings.registry

    if settings.multiprocess_enabled:
        registry = CollectorRegistry()
        MultiProcessCollector(                                                      # type: ignore[no-untyped-call]
            registry,
            path=settings.multiprocess_dir,
        )

    # Bake output
    return exposition.bake_output(
        registry=registry,
        accept_header=environ.get('HTTP_ACCEPT'),
        accept_encoding_header=environ.get('HTTP_ACCEPT_ENCODING'),
        disable_compression=settings.server_disable_compression,
    )
