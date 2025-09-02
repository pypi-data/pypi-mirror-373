"""CELERY CONTROL conf."""
import os
from pathlib import Path
from typing import Any, Callable, Generic, Type, TypeVar

import filelock
from celery.worker.consumer import Consumer
from prometheus_client import CollectorRegistry

FieldType = TypeVar('FieldType')


class Field(Generic[FieldType]):

    def __init__(self) -> None:
        self.name: str = ''
        self._value: FieldType

    def __get__(self: 'Field[FieldType]', instance: Any, owner: Type[Any]) -> FieldType:
        try:
            return self._value
        except AttributeError as error:
            raise RuntimeError('{name} is not set'.format(name=self.name)) from error

    def __set__(self: 'Field[FieldType]', instance: Any, value: FieldType) -> None:
        self._value = value

    def __set_name__(self: 'Field[FieldType]', owner: Type[Any], name: str) -> None:
        self.name = name


# noinspection PyClassHasNoInit
class State(object):
    worker_id = Field[int]()
    worker_id_lock = Field[filelock.AcquireReturnProxy | None]()       # noqa: WPS465
    worker_process_identifier = Field[str]()
    worker_name = Field[str]()
    worker_concurrency = Field[int]()
    consumer = Field[Consumer]()

    # Tasks seen by worker
    tasks_seen: set[str] = set()


# noinspection PyClassHasNoInit
class Settings(object):

    def __init__(self) -> None:
        self._multiproc_enabled: bool | None = None
        self._multiproc_dir_locks: str | None = None

    registry = Field[CollectorRegistry]()

    server_host = Field[str]()
    server_port = Field[int]()
    server_disable_compression = Field[bool]()

    tracker_enabled: bool = False
    tracker_daemon_interval = Field[int]()
    tracker_application_callback: Callable[[], None] | None = None

    multiprocess_dir: str | None = os.environ.get('PROMETHEUS_MULTIPROC_DIR', None)

    @property
    def multiprocess_enabled(self) -> bool:
        if self._multiproc_enabled is None:
            self._multiproc_enabled = self.multiprocess_dir is not None and os.path.isdir(self.multiprocess_dir)

        return self._multiproc_enabled

    @property
    def multiprocess_dir_locks(self) -> str | None:
        if not self.multiprocess_enabled or not self.multiprocess_dir:
            return None

        if self._multiproc_dir_locks is None:
            self._multiproc_dir_locks = os.path.join(self.multiprocess_dir, 'locks')

            # create directory if not exists
            Path(self._multiproc_dir_locks).mkdir(parents=True, exist_ok=True)

        return self._multiproc_dir_locks


state = State()

settings = Settings()
