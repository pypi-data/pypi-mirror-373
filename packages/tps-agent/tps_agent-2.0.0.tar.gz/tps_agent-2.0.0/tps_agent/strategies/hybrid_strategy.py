"""Hybrid monitoring strategy (Collector + Grafana)."""

import logging
from typing import Any, Dict

from ..models import Metric
from .base import MonitoringStrategy
from .collector_strategy import CollectorStrategy
from .prometheus_strategy import PrometheusStrategy

logger = logging.getLogger(__name__)


class HybridStrategy(MonitoringStrategy):
    """Strategy for TPS Agent -> TPS Collector -> Grafana monitoring.

    This strategy combines both collector and Prometheus strategies,
    sending metrics to both TPS Collector and Prometheus simultaneously.
    """

    def __init__(
        self,
        server_id: str,
        collector_url: str,
        prometheus_port: int = 8000,
        collector_timeout: int = 30,
        transmission_interval: int = 30,
        max_local_metrics: int = 10000,
        batch_size: int = 100,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
        local_retention_minutes: int = 60,
        enable_local_storage: bool = True,
        **kwargs,
    ):
        """Initialize hybrid strategy.

        Args:
            server_id: Unique identifier for this server
            collector_url: URL of the TPS Collector server
            prometheus_port: Port to expose Prometheus metrics on
            collector_timeout: Timeout for collector requests in seconds
            transmission_interval: Interval between metric transmissions in seconds
            max_local_metrics: Maximum number of metrics to store locally
            batch_size: Number of metrics to send in each batch
            max_retries: Maximum number of retry attempts
            retry_backoff: Backoff multiplier for retries
            local_retention_minutes: How long to retain metrics locally
            enable_local_storage: Whether to enable local file storage
        """
        super().__init__(server_id, **kwargs)

        # Initialize both strategies
        self.collector_strategy = CollectorStrategy(
            server_id=server_id,
            collector_url=collector_url,
            collector_timeout=collector_timeout,
            transmission_interval=transmission_interval,
            max_local_metrics=max_local_metrics,
            batch_size=batch_size,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            local_retention_minutes=local_retention_minutes,
            enable_local_storage=enable_local_storage,
        )

        self.prometheus_strategy = PrometheusStrategy(
            server_id=server_id, prometheus_port=prometheus_port
        )

    def initialize(self) -> bool:
        """Initialize the hybrid strategy."""
        logger.info(f"Initializing HybridStrategy for server_id: {self.server_id}")

        # Initialize collector strategy
        collector_success = self.collector_strategy.initialize()
        if not collector_success:
            logger.warning("Failed to initialize collector strategy")

        # Initialize Prometheus strategy
        prometheus_success = self.prometheus_strategy.initialize()
        if not prometheus_success:
            logger.warning("Failed to initialize Prometheus strategy")

        # Strategy is considered initialized if at least one sub-strategy works
        self._initialized = collector_success or prometheus_success

        if self._initialized:
            logger.info(
                f"HybridStrategy initialized (collector: {collector_success}, prometheus: {prometheus_success})"
            )
        else:
            logger.error(
                "HybridStrategy failed to initialize - both sub-strategies failed"
            )

        return self._initialized

    def record_metric(self, metric: Metric) -> None:
        """Record a metric using hybrid strategy."""
        if not self._initialized:
            logger.warning("HybridStrategy not initialized, skipping metric")
            return

        # Ensure server_id is set
        metric.server_id = self.server_id

        # Record to collector strategy if initialized
        if self.collector_strategy.is_initialized():
            try:
                self.collector_strategy.record_metric(metric)
            except Exception as e:
                logger.error(f"Error recording metric to collector: {e}")

        # Record to Prometheus strategy if initialized
        if self.prometheus_strategy.is_initialized():
            try:
                self.prometheus_strategy.record_metric(metric)
            except Exception as e:
                logger.error(f"Error recording metric to Prometheus: {e}")

        logger.debug(f"Recorded hybrid metric: {metric.gateway}/{metric.endpoint}")

    def get_stats(self) -> Dict[str, Any]:
        """Get hybrid strategy statistics."""
        stats = {
            "strategy": "hybrid",
            "server_id": self.server_id,
            "initialized": self._initialized,
        }

        # Get stats from sub-strategies
        if self.collector_strategy.is_initialized():
            stats["collector"] = self.collector_strategy.get_stats()
        else:
            stats["collector"] = {"status": "not_initialized"}

        if self.prometheus_strategy.is_initialized():
            stats["prometheus"] = self.prometheus_strategy.get_stats()
        else:
            stats["prometheus"] = {"status": "not_initialized"}

        return stats

    def cleanup(self) -> None:
        """Clean up hybrid strategy resources."""
        logger.info("Cleaning up HybridStrategy")

        # Cleanup both strategies
        if self.collector_strategy:
            try:
                self.collector_strategy.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up collector strategy: {e}")

        if self.prometheus_strategy:
            try:
                self.prometheus_strategy.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up Prometheus strategy: {e}")

        self._initialized = False
