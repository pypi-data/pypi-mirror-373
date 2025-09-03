import pybreaker

from .external_errors import NamedCircuitBreakerError


def call_with_breaker(breaker: pybreaker.CircuitBreaker, func):
    @breaker
    def wrapped():
        return func()
    return wrapped()

class NamedCircuitBreaker(pybreaker.CircuitBreaker):
    def call(self, func, *args, **kwargs):
        if self._state.name == "open":
            raise NamedCircuitBreakerError(self._name)

        return super().call(func, *args, **kwargs)


