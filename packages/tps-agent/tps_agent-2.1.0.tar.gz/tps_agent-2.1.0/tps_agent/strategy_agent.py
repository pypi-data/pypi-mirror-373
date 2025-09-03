"""Simplified TPS Agent using Strategy Pattern."""

import logging
import threading
from typing import Any, Dict, Optional

from .models import Metric
from .strategies.base import MonitoringStrategy

logger = logging.getLogger(__name__)


class StrategyBasedTPSAgent:
    """Simplified TPS Agent that uses monitoring strategies.

    This agent is much simpler than the original TPSAgent as it delegates
    all monitoring logic to specific strategy implementations.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.strategy: Optional[MonitoringStrategy] = None
        self._initialized = True

    def configure(self, strategy: MonitoringStrategy) -> bool:
        """Configure the agent with a monitoring strategy.

        Args:
            strategy: The monitoring strategy to use

        Returns:
            True if configuration succeeded, False otherwise
        """
        self.strategy = strategy

        # Initialize the strategy
        if self.strategy.initialize():
            logger.info(
                f"StrategyBasedTPSAgent configured with {type(strategy).__name__}"
            )
            return True
        else:
            logger.error(f"Failed to initialize {type(strategy).__name__}")
            self.strategy = None
            return False

    def record_metric(self, metric: Metric) -> None:
        """Record a single metric using the configured strategy.

        Args:
            metric: The metric to record
        """
        if not self.strategy:
            logger.warning("No monitoring strategy configured, skipping metric")
            return

        try:
            self.strategy.record_metric(metric)
        except Exception as e:
            logger.error(f"Error recording metric: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from the configured strategy.

        Returns:
            Dictionary containing agent and strategy statistics
        """
        if not self.strategy:
            return {"error": "No monitoring strategy configured"}

        try:
            return self.strategy.get_stats()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    def cleanup(self) -> None:
        """Clean up agent resources."""
        if self.strategy:
            try:
                self.strategy.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.strategy = None


# Global instance
_global_strategy_agent = StrategyBasedTPSAgent()


def configure_strategy_agent(strategy: MonitoringStrategy) -> bool:
    """Configure the global strategy-based TPS agent instance.

    Args:
        strategy: The monitoring strategy to use

    Returns:
        True if configuration succeeded, False otherwise
    """
    return _global_strategy_agent.configure(strategy)


def get_strategy_agent() -> StrategyBasedTPSAgent:
    """Get the global strategy-based TPS agent instance.

    Returns:
        The global StrategyBasedTPSAgent instance
    """
    return _global_strategy_agent
