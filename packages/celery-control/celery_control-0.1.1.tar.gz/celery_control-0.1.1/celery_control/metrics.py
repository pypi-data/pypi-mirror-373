"""
Metrics.

This module contains instances of prometheus client metrics.
"""
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


def make_task_runtime_histogram(buckets: tuple[float, ...] | None = None) -> Histogram:
    return Histogram(
        name='celery_task_runtime_seconds',
        documentation='Task runtime.',
        labelnames=['worker', 'task'],
        buckets=buckets or Histogram.DEFAULT_BUCKETS,
        registry=None,
    )


task_published_total = Counter(
    name='celery_task_published',
    documentation='Number of published tasks.',
    labelnames=['task'],
    registry=None,
)

task_runtime_seconds = make_task_runtime_histogram()

task_accepted_total = Counter(
    name='celery_task_accepted',
    documentation='Number of accepted tasks.',
    labelnames=['worker', 'task'],
    registry=None,
)
task_succeeded_total = Counter(
    name='celery_task_succeeded',
    documentation='Number of tasks successes.',
    labelnames=['worker', 'task'],
    registry=None,
)
task_failed_total = Counter(
    name='celery_task_failed',
    documentation='Number of tasks failures.',
    labelnames=['worker', 'task', 'exception'],
    registry=None,
)
task_retried_total = Counter(
    name='celery_task_retried',
    documentation='Number of tasks retries.',
    labelnames=['worker', 'task', 'exception'],
    registry=None,
)
task_internal_error_total = Counter(
    name='celery_task_internal_errors',
    documentation='Number of tasks internal errors.',
    labelnames=['worker', 'task', 'exception'],
    registry=None,
)
task_rejected_total = Counter(
    name='celery_task_rejected',
    documentation='Number of tasks rejections.',
    labelnames=['worker', 'task', 'requeue'],
    registry=None,
)
task_unknown_total = Counter(
    name='celery_task_unknown',
    documentation='Number of unknown tasks.',
    labelnames=['worker'],
    registry=None,
)
task_revoked_total = Counter(
    name='celery_task_revoked',
    documentation='Number of revoked tasks.',
    labelnames=['worker', 'task', 'terminated', 'expired'],
    registry=None,
)
task_prefetched = Gauge(
    name='celery_task_prefetched',
    documentation='Number of tasks currently prefetched at a worker.',
    labelnames=['worker', 'task'],
    registry=None,
    multiprocess_mode='livemostrecent',
)
task_waiting = Gauge(
    name='celery_task_waiting',
    documentation='Number of tasks currently waiting at a worker.',
    labelnames=['worker', 'task'],
    registry=None,
    multiprocess_mode='livemostrecent',
)
task_active = Gauge(
    name='celery_task_active',
    documentation='Number of tasks currently active at a worker.',
    labelnames=['worker', 'task'],
    registry=None,
    multiprocess_mode='livemostrecent',
)
task_scheduled = Gauge(
    name='celery_task_scheduled',
    documentation='Number of tasks currently scheduled at a worker.',
    labelnames=['worker', 'task'],
    registry=None,
    multiprocess_mode='livemostrecent',
)

worker_online = Gauge(
    name='celery_worker_online',
    documentation='Worker online status',
    labelnames=['worker'],
    registry=None,
    multiprocess_mode='livemostrecent',
)

message_rejected_total = Counter(
    name='celery_message_rejected',
    documentation='Number of message rejections.',
    labelnames=['worker'],
    registry=None,
)


def register_worker_metrics(                                            # noqa: WPS213
    registry: CollectorRegistry,
    task_runtime_buckets: tuple[float, ...] | None = None,
) -> None:
    registry.register(task_published_total)

    global task_runtime_seconds                                         # noqa: WPS420
    if task_runtime_buckets is not None:
        task_runtime_seconds = make_task_runtime_histogram(             # noqa: WPS442
            task_runtime_buckets,
        )

    registry.register(task_runtime_seconds)
    registry.register(task_accepted_total)
    registry.register(task_succeeded_total)
    registry.register(task_failed_total)
    registry.register(task_retried_total)
    registry.register(task_internal_error_total)
    registry.register(task_rejected_total)
    registry.register(task_unknown_total)
    registry.register(task_revoked_total)
    registry.register(task_prefetched)
    registry.register(task_waiting)
    registry.register(task_active)
    registry.register(task_scheduled)
    registry.register(worker_online)
    registry.register(message_rejected_total)


def register_publisher_metrics(registry: CollectorRegistry) -> None:
    registry.register(task_published_total)
