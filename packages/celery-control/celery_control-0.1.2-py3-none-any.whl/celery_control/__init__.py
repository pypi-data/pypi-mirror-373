# flake8: noqa
"""
The library for setup prometheus client's metrics on worker and publisher side.
"""
from .setup import setup_publisher, setup_worker

__all__ = [
    'setup_publisher',
    'setup_worker',
]
