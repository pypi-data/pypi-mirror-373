"""This module provides overridden wsgiref classes."""
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Thread per request HTTP server."""

    # Make worker threads "fire and forget". Beginning with Python 3.7 this
    # prevents a memory leak because ``ThreadingMixIn`` starts to gather all
    # non-daemon threads in a list in order to join on them at server close.
    daemon_threads = True


class SilentHandler(WSGIRequestHandler):
    """WSGI handler that does not log requests."""

    # noinspection PyShadowingBuiltins
    def log_message(self, format, *args) -> None:   # type: ignore[no-untyped-def] # noqa: WPS125
        """Log nothing."""
