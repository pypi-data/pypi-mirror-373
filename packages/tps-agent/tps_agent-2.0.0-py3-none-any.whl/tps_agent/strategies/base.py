"""Base monitoring strategy interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..models import Metric


class MonitoringStrategy(ABC):
    """Abstract base class for monitoring strategies."""

    def __init__(self, server_id: str, **kwargs):
        """Initialize the monitoring strategy.

        Args:
            server_id: Unique identifier for this server/application
            **kwargs: Strategy-specific configuration options
        """
        self.server_id = server_id
        self._initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the monitoring strategy.

        Returns:
            True if initialization succeeded, False otherwise
        """
        pass

    @abstractmethod
    def record_metric(self, metric: Metric) -> None:
        """Record a metric using this strategy.

        Args:
            metric: The metric to record
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics from this strategy.

        Returns:
            Dictionary containing strategy statistics
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by this strategy."""
        pass

    def is_initialized(self) -> bool:
        """Check if strategy is initialized."""
        return self._initialized
