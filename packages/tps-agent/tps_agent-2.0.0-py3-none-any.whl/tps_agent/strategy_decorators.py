"""Strategy-based decorators for TPS measurement and throttling."""

import asyncio
import functools
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union

from .models import Metric
from .strategy_agent import get_strategy_agent


def measure_tps_strategy(
    gateway: str, endpoint: str, tags: Optional[Dict[str, str]] = None
):
    """Decorator to measure TPS using strategy-based agent.

    Args:
        gateway: Gateway name (e.g., 'payment_api', 'user_service')
        endpoint: Endpoint name (e.g., 'process_payment', 'get_user')
        tags: Optional tags to attach to the metric

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                error_msg = None
                success = True

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    # Record metric
                    duration_ms = (time.time() - start_time) * 1000
                    metric = Metric(
                        gateway=gateway,
                        endpoint=endpoint,
                        server_id="",  # Will be set by strategy
                        timestamp=datetime.now(),
                        duration_ms=duration_ms,
                        success=success,
                        error=error_msg,
                        tags=tags,
                    )

                    agent = get_strategy_agent()
                    agent.record_metric(metric)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                error_msg = None
                success = True

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    # Record metric
                    duration_ms = (time.time() - start_time) * 1000
                    metric = Metric(
                        gateway=gateway,
                        endpoint=endpoint,
                        server_id="",  # Will be set by strategy
                        timestamp=datetime.now(),
                        duration_ms=duration_ms,
                        success=success,
                        error=error_msg,
                        tags=tags,
                    )

                    agent = get_strategy_agent()
                    agent.record_metric(metric)

            return sync_wrapper

    return decorator


# Global throttling state per gateway+endpoint combination
# Structure: {gateway:endpoint -> {'requests': [(timestamp, )], 'window_start': float}}
_throttle_state: Dict[str, Dict[str, Any]] = {}


def throttle(
    gateway: str, endpoint: str, max_tps: Union[int, float], window_seconds: float = 1.0
):
    """Decorator to throttle function calls per gateway+endpoint combination using sliding window.

    Args:
        gateway: Gateway name for throttling
        endpoint: Endpoint name for throttling
        max_tps: Maximum transactions per second allowed for this gateway+endpoint
        window_seconds: Time window in seconds for TPS calculation (default: 1.0)

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        throttle_key = f"{gateway}:{endpoint}"

        # Initialize throttle state for this gateway+endpoint if not exists
        if throttle_key not in _throttle_state:
            _throttle_state[throttle_key] = {
                "requests": [],  # List of request timestamps
                "window_start": 0.0,
            }

        def _wait_for_slot():
            """Calculate how long to wait before the next request can be made."""
            current_time = time.time()
            state = _throttle_state[throttle_key]

            # Clean up old requests outside the window
            cutoff_time = current_time - window_seconds
            state["requests"] = [
                req_time for req_time in state["requests"] if req_time > cutoff_time
            ]

            # Check if we're under the limit
            max_requests_in_window = int(max_tps * window_seconds)
            if len(state["requests"]) < max_requests_in_window:
                # We're under the limit, can proceed immediately
                state["requests"].append(current_time)
                return 0.0

            # We're at the limit, need to wait until the oldest request expires
            oldest_request = min(state["requests"])
            wait_time = oldest_request + window_seconds - current_time

            # Add small buffer to avoid race conditions
            return max(0.0, wait_time + 0.001)

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                # Wait for available slot in TPS limit
                wait_time = _wait_for_slot()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # After waiting, record the actual request time
                    _throttle_state[throttle_key]["requests"].append(time.time())

                return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                # Wait for available slot in TPS limit
                wait_time = _wait_for_slot()
                if wait_time > 0:
                    time.sleep(wait_time)
                    # After waiting, record the actual request time
                    _throttle_state[throttle_key]["requests"].append(time.time())

                return func(*args, **kwargs)

            return sync_wrapper

    return decorator
