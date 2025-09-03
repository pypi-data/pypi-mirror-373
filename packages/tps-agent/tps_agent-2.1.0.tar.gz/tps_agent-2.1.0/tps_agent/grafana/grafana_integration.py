"""Grafana integration module for TPS Agent."""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class MonitoringMode(Enum):
    """Monitoring mode enumeration."""

    COLLECTOR = "collector"  # Send to TPS Collector
    GRAFANA = "grafana"  # Export to Prometheus/Grafana
    BOTH = "both"  # Send to both


class GrafanaIntegration:
    """Manages Grafana integration for TPS Agent."""

    def __init__(
        self,
        mode: MonitoringMode = MonitoringMode.COLLECTOR,
        prometheus_port: int = 8000,
    ):
        """Initialize Grafana integration.

        Args:
            mode: Monitoring mode (collector/grafana/both)
            prometheus_port: Port for Prometheus metrics server
        """
        self.mode = mode
        self.prometheus_port = prometheus_port
        self._prometheus_exporter = None

        # Initialize based on mode
        if self.mode in (MonitoringMode.GRAFANA, MonitoringMode.BOTH):
            self._init_prometheus_exporter()

    def _init_prometheus_exporter(self):
        """Initialize Prometheus exporter if needed."""
        try:
            from .prometheus_exporter import init_prometheus_exporter  # noqa: F401

            # Don't start yet - wait for agent configuration
            logger.info("Prometheus exporter ready for initialization")
        except ImportError:
            logger.warning("prometheus_client not available - Grafana mode disabled")
            if self.mode == MonitoringMode.GRAFANA:
                self.mode = MonitoringMode.COLLECTOR
                logger.info("Fallback to collector mode")
            elif self.mode == MonitoringMode.BOTH:
                logger.info("Using collector mode only")

    def configure(self, server_id: str, collector_url: str = ""):
        """Configure integration with agent details.

        Args:
            server_id: Agent server ID
            collector_url: TPS Collector URL
        """
        if self.mode in (MonitoringMode.GRAFANA, MonitoringMode.BOTH):
            try:
                from .prometheus_exporter import init_prometheus_exporter

                self._prometheus_exporter = init_prometheus_exporter(
                    port=self.prometheus_port,
                    server_id=server_id,
                    collector_url=collector_url,
                )
                logger.info(f"Prometheus exporter configured for {server_id}")
            except Exception as e:
                logger.error(f"Failed to configure Prometheus exporter: {e}")

    def record_metric(
        self,
        gateway: str,
        endpoint: str,
        duration_ms: float,
        server_id: str,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Record metric to appropriate monitoring system(s).

        Args:
            gateway: Gateway name
            endpoint: Endpoint name
            duration_ms: Duration in milliseconds
            server_id: Server ID
            success: Whether request was successful
            error: Error message if any
        """
        # Convert to seconds for Prometheus
        duration_sec = duration_ms / 1000.0
        status = "success" if success else "error"
        error_type = "Exception" if error else None

        # Send to Prometheus/Grafana if enabled
        if (
            self.mode in (MonitoringMode.GRAFANA, MonitoringMode.BOTH)
            and self._prometheus_exporter
        ):
            try:
                self._prometheus_exporter.record_request(
                    gateway=gateway,
                    endpoint=endpoint,
                    duration=duration_sec,
                    server_id=server_id,
                    status=status,
                    error_type=error_type,
                )
            except Exception as e:
                logger.error(f"Failed to record metric to Prometheus: {e}")

        # Send to TPS Collector if enabled
        if self.mode in (MonitoringMode.COLLECTOR, MonitoringMode.BOTH):
            try:
                from ..agent import record_metric

                record_metric(
                    gateway=gateway,
                    endpoint=endpoint,
                    duration_ms=duration_ms,
                    success=success,
                    error=error,
                )
            except Exception as e:
                logger.error(f"Failed to record metric to collector: {e}")

    def get_metrics_endpoint(self) -> Optional[str]:
        """Get Prometheus metrics endpoint URL."""
        if self._prometheus_exporter:
            return f"http://localhost:{self.prometheus_port}/metrics"
        return None

    def is_grafana_enabled(self) -> bool:
        """Check if Grafana mode is enabled."""
        return self.mode in (MonitoringMode.GRAFANA, MonitoringMode.BOTH)

    def is_collector_enabled(self) -> bool:
        """Check if Collector mode is enabled."""
        return self.mode in (MonitoringMode.COLLECTOR, MonitoringMode.BOTH)

    def close(self):
        """Close integration and cleanup resources."""
        if self._prometheus_exporter:
            try:
                from .prometheus_exporter import close_prometheus_exporter

                close_prometheus_exporter()
                self._prometheus_exporter = None
                logger.info("Prometheus exporter closed")
            except Exception as e:
                logger.error(f"Error closing Prometheus exporter: {e}")


# Global integration instance
_integration: Optional[GrafanaIntegration] = None


def get_grafana_integration() -> Optional[GrafanaIntegration]:
    """Get global Grafana integration instance."""
    return _integration


def init_grafana_integration(
    mode: MonitoringMode = MonitoringMode.COLLECTOR, prometheus_port: int = 8000
) -> GrafanaIntegration:
    """Initialize global Grafana integration.

    Args:
        mode: Monitoring mode
        prometheus_port: Prometheus metrics port

    Returns:
        GrafanaIntegration instance
    """
    global _integration
    if _integration is None:
        _integration = GrafanaIntegration(mode=mode, prometheus_port=prometheus_port)
        logger.info(f"Grafana integration initialized in {mode.value} mode")
    return _integration
