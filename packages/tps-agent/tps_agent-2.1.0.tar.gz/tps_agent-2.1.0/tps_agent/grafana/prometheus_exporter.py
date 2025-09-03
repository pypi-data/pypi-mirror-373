"""Prometheus metrics exporter for Grafana integration."""

import logging
import threading
from typing import Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Exports TPS Agent metrics to Prometheus format for Grafana."""

    def __init__(self, port: int = 8000, registry: Optional[CollectorRegistry] = None):
        """Initialize Prometheus exporter.

        Args:
            port: Port to serve metrics on
            registry: Custom registry (optional)
        """
        self.port = port
        self.registry = registry or CollectorRegistry()
        self.server_started = False
        self._lock = threading.Lock()

        # Define metrics with proper labels
        self.request_count = Counter(
            "tps_requests_total",
            "Total number of requests",
            ["gateway", "endpoint", "status", "server_id"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "tps_request_duration_seconds",
            "Request duration in seconds",
            ["gateway", "endpoint", "server_id"],
            registry=self.registry,
            buckets=(
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        self.active_requests = Gauge(
            "tps_active_requests",
            "Number of active requests",
            ["gateway", "endpoint", "server_id"],
            registry=self.registry,
        )

        self.error_count = Counter(
            "tps_errors_total",
            "Total number of errors",
            ["gateway", "endpoint", "error_type", "server_id"],
            registry=self.registry,
        )

        # Agent info metric
        self.agent_info = Gauge(
            "tps_agent_info",
            "TPS Agent information",
            ["server_id", "version", "collector_url"],
            registry=self.registry,
        )

    def start_server(self):
        """Start Prometheus metrics server."""
        with self._lock:
            if not self.server_started:
                try:
                    start_http_server(self.port, registry=self.registry)
                    self.server_started = True
                    logger.info(
                        f"Prometheus metrics server started on port {self.port}"
                    )
                except Exception as e:
                    logger.error(f"Failed to start Prometheus server: {e}")
                    raise

    def record_request(
        self,
        gateway: str,
        endpoint: str,
        duration: float,
        server_id: str,
        status: str = "success",
        error_type: Optional[str] = None,
    ):
        """Record a request metric.

        Args:
            gateway: Gateway name
            endpoint: Endpoint name
            duration: Request duration in seconds
            server_id: Server/agent ID
            status: Request status (success/error)
            error_type: Error type if status is error
        """
        labels = {"gateway": gateway, "endpoint": endpoint, "server_id": server_id}
        status_labels = {**labels, "status": status}

        # Record metrics
        self.request_count.labels(**status_labels).inc()
        self.request_duration.labels(**labels).observe(duration)

        if error_type:
            self.error_count.labels(**labels, error_type=error_type).inc()

    def inc_active_requests(self, gateway: str, endpoint: str, server_id: str):
        """Increment active requests counter."""
        self.active_requests.labels(
            gateway=gateway, endpoint=endpoint, server_id=server_id
        ).inc()

    def dec_active_requests(self, gateway: str, endpoint: str, server_id: str):
        """Decrement active requests counter."""
        self.active_requests.labels(
            gateway=gateway, endpoint=endpoint, server_id=server_id
        ).dec()

    def set_agent_info(
        self, server_id: str, version: str = "2.0.0", collector_url: str = ""
    ):
        """Set agent information metric."""
        self.agent_info.labels(
            server_id=server_id, version=version, collector_url=collector_url
        ).set(1)


# Global exporter instance
_exporter: Optional[PrometheusExporter] = None
_lock = threading.Lock()


def get_prometheus_exporter() -> Optional[PrometheusExporter]:
    """Get global Prometheus exporter instance."""
    return _exporter


def init_prometheus_exporter(
    port: int = 8000, server_id: str = "unknown", collector_url: str = ""
) -> PrometheusExporter:
    """Initialize Prometheus exporter with custom configuration."""
    global _exporter
    with _lock:
        if _exporter is None:
            _exporter = PrometheusExporter(port=port)
            _exporter.start_server()
            _exporter.set_agent_info(server_id=server_id, collector_url=collector_url)
            logger.info(f"Prometheus exporter initialized for agent {server_id}")
    return _exporter


def close_prometheus_exporter():
    """Close Prometheus exporter."""
    global _exporter
    with _lock:
        _exporter = None
