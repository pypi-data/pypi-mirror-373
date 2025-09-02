"""Prometheus monitoring strategy."""

import logging
from typing import Any, Dict, Optional

from ..models import Metric
from .base import MonitoringStrategy

logger = logging.getLogger(__name__)


class PrometheusStrategy(MonitoringStrategy):
    """Strategy for TPS Agent -> Prometheus -> Grafana monitoring."""

    def __init__(self, server_id: str, prometheus_port: int = 8000, **kwargs):
        """Initialize Prometheus strategy.

        Args:
            server_id: Unique identifier for this server
            prometheus_port: Port to expose Prometheus metrics on
        """
        super().__init__(server_id, **kwargs)
        self.prometheus_port = prometheus_port
        self.prometheus_exporter: Optional[Any] = None

    def initialize(self) -> bool:
        """Initialize the Prometheus strategy."""
        try:
            # Try to import Prometheus dependencies
            try:
                from ..grafana.prometheus_exporter import init_prometheus_exporter
            except ImportError:
                logger.error(
                    "Prometheus dependencies not available. Install with: pip install prometheus_client"
                )
                return False

            # Initialize Prometheus exporter
            self.prometheus_exporter = init_prometheus_exporter(
                port=self.prometheus_port,
                server_id=self.server_id,
                collector_url=None,  # Not needed for Prometheus-only mode
            )

            self._initialized = True
            logger.info(
                f"PrometheusStrategy initialized on port {self.prometheus_port} for server_id: {self.server_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize PrometheusStrategy: {e}")
            return False

    def record_metric(self, metric: Metric) -> None:
        """Record a metric using Prometheus strategy."""
        if not self._initialized or not self.prometheus_exporter:
            logger.warning("PrometheusStrategy not initialized, skipping metric")
            return

        # Ensure server_id is set
        metric.server_id = self.server_id

        # Convert metric to Prometheus format
        duration_sec = metric.duration_ms / 1000.0
        status = "success" if metric.success else "error"
        error_type = metric.error if metric.error else None

        # Record metric with Prometheus exporter
        try:
            self.prometheus_exporter.record_request(
                gateway=metric.gateway,
                endpoint=metric.endpoint,
                duration=duration_sec,
                server_id=self.server_id,
                status=status,
                error_type=error_type,
            )
            logger.debug(
                f"Recorded Prometheus metric: {metric.gateway}/{metric.endpoint}"
            )

        except Exception as e:
            logger.error(f"Failed to record Prometheus metric: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get Prometheus strategy statistics."""
        stats = {
            "strategy": "prometheus",
            "server_id": self.server_id,
            "prometheus_port": self.prometheus_port,
            "initialized": self._initialized,
        }

        if self.prometheus_exporter:
            stats["metrics_endpoint"] = (
                f"http://localhost:{self.prometheus_port}/metrics"
            )
            # Try to get metrics count if available
            try:
                stats["exporter_status"] = "active"
            except Exception:
                stats["exporter_status"] = "unknown"

        return stats

    def cleanup(self) -> None:
        """Clean up Prometheus strategy resources."""
        logger.info("Cleaning up PrometheusStrategy")

        if self.prometheus_exporter:
            try:
                # Try to cleanup Prometheus exporter if it has cleanup method
                if hasattr(self.prometheus_exporter, "cleanup"):
                    self.prometheus_exporter.cleanup()
            except Exception as e:
                logger.warning(f"Error during Prometheus exporter cleanup: {e}")

            self.prometheus_exporter = None

        self._initialized = False
