"""This module provides method for generating lazy observable class."""
from typing import Type, TypeVar

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary
from prometheus_client.metrics import MetricWrapperBase

Metric = TypeVar('Metric', Counter, Gauge, Histogram, Summary)


def make_lazy_observable_class(base: Type[Metric]) -> Type[Metric]:
    """Create lazy observable class."""

    class LazyObservable(base):                 # noqa: WPS431

        def __init__(self, *args, **kwargs):
            self._flag = False
            super().__init__(*args, **kwargs)

        # noinspection PyProtectedMember
        def _is_observable(self):
            if not self._flag:
                return False

            return super()._is_observable()

        # noinspection PyProtectedMember
        def _raise_if_not_observable(self):
            if not self._flag:
                self._metric_init()
                self._flag = True

            # noinspection PyProtectedMember
            super()._raise_if_not_observable()

    return LazyObservable


# noinspection PyProtectedMember
def get_observable_metric_names(registry: CollectorRegistry) -> list[str]:
    """Get list of observable metric names."""
    names = []
    for collector in registry._collector_to_names.keys():                       # noqa: WPS437
        if isinstance(collector, MetricWrapperBase):
            if collector._is_observable():                                      # noqa: WPS437
                name = getattr(collector, '_name', None)
                if name:
                    names.append(name)

    return names
