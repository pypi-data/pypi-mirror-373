"""This module provides methods for generate response output."""
import gzip
from typing import Callable

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from prometheus_client.openmetrics import exposition as openmetrics

from celery_control.server.types import TypeOutput


def bake_output(
    registry: CollectorRegistry,
    accept_header: str | None,
    accept_encoding_header: str | None,
    disable_compression: bool | None,
) -> TypeOutput:
    """Bake output for metrics output."""
    # Choose the correct plain text format of the output.
    encoder, content_type = _choose_encoder(accept_header)

    output = encoder(registry)
    headers = [('Content-Type', content_type)]

    # If gzip encoding required, gzip the output.
    if not disable_compression and _gzip_accepted(accept_encoding_header):
        output = gzip.compress(output)
        headers.append(('Content-Encoding', 'gzip'))
    return '200 OK', headers, output


def _choose_encoder(accept_header: str | None) -> tuple[Callable[[CollectorRegistry], bytes], str]:
    accept_header = accept_header or ''
    for accepted in accept_header.split(','):
        if accepted.split(';')[0].strip() == 'application/openmetrics-text':
            return openmetrics.generate_latest, openmetrics.CONTENT_TYPE_LATEST

    return generate_latest, CONTENT_TYPE_LATEST


def _gzip_accepted(accept_encoding_header: str | None) -> bool:
    accept_encoding_header = accept_encoding_header or ''
    for accepted in accept_encoding_header.split(','):
        if accepted.split(';')[0].strip().lower() == 'gzip':
            return True
    return False
