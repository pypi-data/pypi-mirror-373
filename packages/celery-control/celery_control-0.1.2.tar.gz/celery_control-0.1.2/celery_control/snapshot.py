"""This module provides the methods for get snapshots."""
import dataclasses
from typing import Generator

from celery.worker.request import Request
from celery.worker.state import active_requests, reserved_requests
from kombu.asynchronous.timer import Entry, Timer

from celery_control.conf import state


@dataclasses.dataclass
class RequestsSnapshot:           # noqa: WPS306
    """
    This object contains current requests.

    prefetched: Set of all received requests.
    active: Set of executing requests.
    reserved: Set of waiting requests.
    scheduled: Set of scheduled requests.
    """

    prefetched: set[Request]
    active: set[Request]
    waiting: set[Request]
    scheduled: set[Request]


def make_requests_snapshot() -> RequestsSnapshot:
    """Make requests snapshot."""
    prefetched = set(reserved_requests)
    active = set(active_requests)
    waiting = prefetched - active
    scheduled = set(_scheduled())

    return RequestsSnapshot(
        prefetched=prefetched,
        active=active,
        waiting=waiting,
        scheduled=scheduled,
    )


def _scheduled() -> Generator[Request, None, None]:
    timer: Timer = state.consumer.timer

    for waiting in timer.schedule.queue:
        entry: Entry = waiting.entry
        try:
            arg0 = entry.args[0]
        except (IndexError, TypeError):
            continue
        else:
            if isinstance(arg0, Request):
                yield arg0
