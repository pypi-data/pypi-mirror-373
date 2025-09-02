"""Decorators for TPS measurement and throttling."""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from .agent import get_agent, record_metric

F = TypeVar("F", bound=Callable[..., Any])


def measure_tps(
    gateway: str,
    endpoint: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    track_errors: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to measure TPS for a function.

    Args:
        gateway: The gateway/service name for grouping metrics
        endpoint: Optional endpoint name (defaults to module.function)
        tags: Optional additional tags for the metric
        track_errors: Whether to track error messages

    Example:
        @measure_tps(gateway="payment_api", endpoint="process_payment")
        def process_payment(amount):
            # Your code here
            pass
    """

    def decorator(func: F) -> F:
        # Safe access to function attributes
        func_module = getattr(func, "__module__", "<unknown>")
        func_name = getattr(func, "__name__", "<unknown>")
        endpoint_name = endpoint or f"{func_module}.{func_name}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_metrics:
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            error_msg = None
            success = True

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                if track_errors:
                    error_msg = str(e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                record_metric(
                    gateway=gateway,
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    success=success,
                    error=error_msg,
                    tags=tags,
                )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_metrics:
                return await func(*args, **kwargs)

            start_time = time.perf_counter()
            error_msg = None
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                if track_errors:
                    error_msg = str(e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                record_metric(
                    gateway=gateway,
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    success=success,
                    error=error_msg,
                    tags=tags,
                )

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)

    return decorator


class ThrottleException(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, gateway: str, max_tps: float, current_tps: float):
        self.gateway = gateway
        self.max_tps = max_tps
        self.current_tps = current_tps
        super().__init__(
            f"Rate limit exceeded for {gateway}: {current_tps:.2f} > {max_tps:.2f} TPS"
        )


# Simple in-memory throttling (since we don't have Redis in agent)
class SimpleThrottler:
    """Simple in-memory throttling for agent."""

    def __init__(self):
        self._calls = {}  # gateway -> list of timestamps

    def check_rate_limit(
        self, gateway: str, max_tps: float, window_seconds: int = 1
    ) -> bool:
        """Check if rate limit allows this call."""
        now = time.time()
        window_start = now - window_seconds

        # Clean old calls
        if gateway in self._calls:
            self._calls[gateway] = [
                t for t in self._calls[gateway] if t >= window_start
            ]
        else:
            self._calls[gateway] = []

        # Check rate
        current_calls = len(self._calls[gateway])
        current_tps = current_calls / window_seconds

        if current_tps >= max_tps:
            return False

        # Record this call
        self._calls[gateway].append(now)
        return True

    def get_current_tps(self, gateway: str, window_seconds: int = 1) -> float:
        """Get current TPS for a gateway."""
        now = time.time()
        window_start = now - window_seconds

        if gateway not in self._calls:
            return 0.0

        recent_calls = [t for t in self._calls[gateway] if t >= window_start]
        return len(recent_calls) / window_seconds


# Global throttler instance
_throttler = SimpleThrottler()


def throttle(gateway: str, max_tps: float, window_seconds: int = 1) -> Callable[[F], F]:
    """
    Decorator to throttle function calls based on TPS limit.

    Args:
        gateway: The gateway/service name for throttling
        max_tps: Maximum transactions per second allowed
        window_seconds: Time window for rate calculation

    Example:
        @throttle(gateway="external_api", max_tps=100)
        def call_external_api():
            # Your code here
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return func(*args, **kwargs)

            if not _throttler.check_rate_limit(gateway, max_tps, window_seconds):
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, max_tps, current_tps)

            return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return await func(*args, **kwargs)

            if not _throttler.check_rate_limit(gateway, max_tps, window_seconds):
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, max_tps, current_tps)

            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)

    return decorator
