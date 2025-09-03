"""Main TPS Agent class for managing metrics collection and transmission."""

import logging
import threading
from datetime import datetime
from typing import Any, Dict, Optional

from .config import AgentConfig
from .models import Metric
from .storage import HybridStorage
from .transmission import CollectorClient, TransmissionManager

logger = logging.getLogger(__name__)


class TPSAgent:
    """Main TPS Agent class - singleton for managing metrics collection."""

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

        self.config: Optional[AgentConfig] = None
        self.storage: Optional[HybridStorage] = None
        self.client: Optional[CollectorClient] = None
        self.transmission_manager: Optional[TransmissionManager] = None
        self.grafana_integration = None
        self._initialized = True

    def configure(self, config: AgentConfig) -> None:
        """Configure the agent with the provided configuration."""
        self.config = config

        # Initialize storage
        self.storage = HybridStorage(
            max_metrics=config.max_local_metrics,
            retention_minutes=config.local_retention_minutes,
            enable_file_storage=config.enable_local_storage,
        )

        # Load any existing metrics from file
        if config.enable_local_storage:
            existing_metrics = self.storage.load_from_file()
            if existing_metrics:
                logger.info(
                    f"Loaded {len(existing_metrics)} existing metrics from file"
                )
                for metric in existing_metrics:
                    self.storage.store_metric(metric)

        # Initialize Grafana integration
        try:
            from .grafana.grafana_integration import (
                MonitoringMode,
                init_grafana_integration,
            )

            mode = MonitoringMode(config.monitoring_mode)
            self.grafana_integration = init_grafana_integration(
                mode=mode, prometheus_port=config.prometheus_port
            )
            self.grafana_integration.configure(
                server_id=config.server_id, collector_url=config.collector_url
            )
            logger.info(f"Grafana integration initialized in {mode.value} mode")
        except Exception as e:
            logger.warning(f"Failed to initialize Grafana integration: {e}")
            self.grafana_integration = None

        # Initialize collector client (only if needed)
        logger.info(
            f"Grafana integration status: {self.grafana_integration is not None}"
        )
        if self.grafana_integration:
            logger.info(
                f"Collector enabled: {self.grafana_integration.is_collector_enabled()}"
            )

        if (
            not self.grafana_integration
            or self.grafana_integration.is_collector_enabled()
        ):
            logger.info("Initializing collector client...")
            self.client = CollectorClient(config)

            # Test connection to collector
            if self.client.test_connection():
                logger.info(
                    f"Successfully connected to collector at {config.collector_url}"
                )
            else:
                logger.warning(
                    f"Failed to connect to collector at {config.collector_url}"
                )
        else:
            logger.info("Skipping collector client initialization (Grafana-only mode)")

        # Initialize transmission manager
        self.transmission_manager = TransmissionManager(
            config, self.storage, self.client
        )
        self.transmission_manager.start()

        logger.info(f"TPS Agent configured for server_id: {config.server_id}")

    def record_metric(self, metric: Metric) -> None:
        """Record a single metric."""
        if not self.config or not self.config.enable_metrics:
            return

        # Ensure server_id is set
        metric.server_id = self.config.server_id

        # Send to Grafana integration if available
        if self.grafana_integration:
            try:
                self.grafana_integration.record_metric(
                    gateway=metric.gateway,
                    endpoint=metric.endpoint,
                    duration_ms=metric.duration_ms,
                    server_id=metric.server_id,
                    success=metric.success,
                    error=metric.error,
                )
            except Exception as e:
                logger.error(f"Failed to record metric to Grafana: {e}")

        # Store metric locally for collector mode (if enabled)
        if (
            not self.grafana_integration
            or self.grafana_integration.is_collector_enabled()
        ):
            if not self.storage:
                logger.warning("Storage not initialized, metric ignored")
                return
            self.storage.store_metric(metric)

        logger.debug(f"Recorded metric: {metric.gateway}.{metric.endpoint}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current agent statistics."""
        if not self.storage:
            return {}

        return {
            "server_id": self.config.server_id if self.config else "unknown",
            "local_metrics_count": self.storage.get_count(),
            "total_metrics_stored": self.storage.get_total_stored(),
            "last_transmission": (
                self.client.last_transmission.isoformat()
                if self.client and self.client.last_transmission
                else None
            ),
            "collector_url": self.config.collector_url if self.config else None,
            "transmission_interval": (
                self.config.transmission_interval if self.config else None
            ),
        }

    def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        logger.info("Shutting down TPS Agent...")

        if self.transmission_manager:
            self.transmission_manager.stop()

        # Try to send remaining metrics
        if self.storage and self.client and self.config:
            remaining_metrics = self.storage.get_metrics()
            if remaining_metrics:
                try:
                    self.client.send_metrics(remaining_metrics)
                    logger.info(
                        f"Sent {len(remaining_metrics)} remaining metrics before shutdown"
                    )
                except Exception as e:
                    logger.error(f"Failed to send remaining metrics: {e}")

        # Close Grafana integration
        if self.grafana_integration:
            try:
                self.grafana_integration.close()
                logger.info("Grafana integration closed")
            except Exception as e:
                logger.error(f"Error closing Grafana integration: {e}")

        logger.info("TPS Agent shutdown complete")


# Global instance
_global_agent = TPSAgent()


def configure_agent(
    collector_url: str,
    server_id: str,
    config: Optional[AgentConfig] = None,
    monitoring_mode: str = "collector",
    prometheus_port: int = 8000,
) -> None:
    """Configure the global TPS agent instance."""
    if config is None:
        # Create config from parameters and environment
        env_config = AgentConfig.from_environment()
        config = AgentConfig(
            server_id=server_id,
            collector_url=collector_url,
            collector_timeout=env_config.collector_timeout,
            max_local_metrics=env_config.max_local_metrics,
            batch_size=env_config.batch_size,
            transmission_interval=env_config.transmission_interval,
            max_retries=env_config.max_retries,
            retry_backoff=env_config.retry_backoff,
            local_retention_minutes=env_config.local_retention_minutes,
            enable_metrics=env_config.enable_metrics,
            enable_throttling=env_config.enable_throttling,
            enable_local_storage=env_config.enable_local_storage,
            monitoring_mode=monitoring_mode,
            prometheus_port=prometheus_port,
        )

    _global_agent.configure(config)


def get_agent() -> TPSAgent:
    """Get the global TPS agent instance."""
    return _global_agent


def record_metric(
    gateway: str,
    endpoint: str,
    duration_ms: float,
    success: bool,
    error: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
) -> None:
    """Record a metric using the global agent."""
    metric = Metric(
        gateway=gateway,
        endpoint=endpoint,
        server_id="",  # Will be set by agent
        timestamp=datetime.now(),
        duration_ms=duration_ms,
        success=success,
        error=error,
        tags=tags,
    )

    _global_agent.record_metric(metric)
