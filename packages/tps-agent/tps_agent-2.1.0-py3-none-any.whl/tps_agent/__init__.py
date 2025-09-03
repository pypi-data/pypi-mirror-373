"""
TPS Agent - Lightweight metrics collection library for distributed TPS monitoring.

This library provides decorators for measuring and throttling TPS (Transactions Per Second)
in distributed applications. It collects metrics locally and periodically sends them
to a centralized tpsCollector server.

Usage:
    from tps_agent import measure_tps, throttle, configure_agent

    # Configure the agent
    configure_agent(collector_url="http://localhost:8080", server_id="web-server-1")

    # Use decorators
    @measure_tps(gateway="payment_api")
    def process_payment():
        # Your code here
        pass

    @throttle(gateway="external_api", max_tps=100)
    def call_external_api():
        # Your code here
        pass
"""

from .agent import TPSAgent, configure_agent, get_agent
from .decorators import measure_tps
from .strategies import CollectorStrategy, HybridStrategy, PrometheusStrategy

# Strategy-based interface (new)
from .strategy_agent import (
    StrategyBasedTPSAgent,
    configure_strategy_agent,
    get_strategy_agent,
)
from .strategy_decorators import measure_tps_strategy, throttle

# Legacy alias for compatibility
throttle_strategy = throttle

__version__ = "2.1.0"
__all__ = [
    # Legacy interface
    "measure_tps",
    "throttle",
    "configure_agent",
    "get_agent",
    "TPSAgent",
    # Strategy-based interface
    "StrategyBasedTPSAgent",
    "configure_strategy_agent",
    "get_strategy_agent",
    "measure_tps_strategy",
    "throttle_strategy",  # throttle_strategy is alias for throttle
    "CollectorStrategy",
    "PrometheusStrategy",
    "HybridStrategy",
]
