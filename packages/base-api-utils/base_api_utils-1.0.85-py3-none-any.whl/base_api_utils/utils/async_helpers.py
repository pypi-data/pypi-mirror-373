from functools import wraps

from .circuit_breaker import NamedCircuitBreakerError
from celery import shared_task
from pybreaker import CircuitBreakerError

def async_task(
    max_retries=5,
    countdown=60,
    retry_backoff_max=600,
    autoretry_for=(ConnectionError, TimeoutError, OSError),
    dont_autoretry_for=(CircuitBreakerError, NamedCircuitBreakerError),
    **celery_kwargs
):
    """
    Generic decorator for Celery tasks

    Args:
        max_retries: Maximum number of retries
        countdown: Base delay in seconds
        retry_backoff_max: Maximum delay in seconds
        autoretry_for: Tuple of exceptions that trigger automatic retries
        dont_autoretry_for: Tuple of exceptions that should NOT be retried
        **celery_kwargs: Additional arguments for @shared_task
    """

    def decorator(func):
        @shared_task(
            bind=True,
            autoretry_for=autoretry_for,
            dont_autoretry_for=dont_autoretry_for,
            retry_backoff=True,
            retry_backoff_max=retry_backoff_max,
            retry_jitter=True,
            retry_kwargs={'max_retries': max_retries, 'countdown': countdown},
            **celery_kwargs
        )
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapper
    return decorator