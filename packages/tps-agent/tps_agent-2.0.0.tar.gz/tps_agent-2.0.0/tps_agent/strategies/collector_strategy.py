"""TPS Collector monitoring strategy."""

import logging
from typing import Any, Dict, Optional

from ..config import AgentConfig
from ..models import Metric
from ..storage import HybridStorage
from ..transmission import CollectorClient, TransmissionManager
from .base import MonitoringStrategy

logger = logging.getLogger(__name__)


class CollectorStrategy(MonitoringStrategy):
    """Strategy for TPS Agent -> TPS Collector -> Dashboard monitoring."""

    def __init__(
        self,
        server_id: str,
        collector_url: str,
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
        """Initialize collector strategy.

        Args:
            server_id: Unique identifier for this server
            collector_url: URL of the TPS Collector server
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

        # Create configuration for this strategy
        self.config = AgentConfig(
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
            enable_metrics=True,
            enable_throttling=True,
            monitoring_mode="collector",
            prometheus_port=8000,  # Not used but required by config
        )

        self.storage: Optional[HybridStorage] = None
        self.client: Optional[CollectorClient] = None
        self.transmission_manager: Optional[TransmissionManager] = None

    def initialize(self) -> bool:
        """Initialize the collector strategy."""
        try:
            # Initialize storage
            self.storage = HybridStorage(
                max_metrics=self.config.max_local_metrics,
                retention_minutes=self.config.local_retention_minutes,
                enable_file_storage=self.config.enable_local_storage,
            )

            # Load existing metrics from file if enabled
            if self.config.enable_local_storage:
                existing_metrics = self.storage.load_from_file()
                if existing_metrics:
                    logger.info(
                        f"Loaded {len(existing_metrics)} existing metrics from file"
                    )
                    for metric in existing_metrics:
                        self.storage.store_metric(metric)

            # Initialize collector client
            self.client = CollectorClient(self.config)

            # Test connection to collector
            if self.client.test_connection():
                logger.info(
                    f"Successfully connected to collector at {self.config.collector_url}"
                )
            else:
                logger.warning(
                    f"Failed to connect to collector at {self.config.collector_url}"
                )
                # Continue anyway - transmission manager will handle retries

            # Initialize transmission manager
            self.transmission_manager = TransmissionManager(
                self.config, self.storage, self.client
            )
            self.transmission_manager.start()

            self._initialized = True
            logger.info(
                f"CollectorStrategy initialized for server_id: {self.server_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize CollectorStrategy: {e}")
            return False

    def record_metric(self, metric: Metric) -> None:
        """Record a metric using collector strategy."""
        if not self._initialized or not self.storage:
            logger.warning("CollectorStrategy not initialized, skipping metric")
            return

        # Ensure server_id is set
        metric.server_id = self.server_id

        # Store metric locally
        self.storage.store_metric(metric)

        logger.debug(f"Recorded metric: {metric.gateway}/{metric.endpoint}")

    def get_stats(self) -> Dict[str, Any]:
        """Get collector strategy statistics."""
        if not self._initialized:
            return {"error": "Strategy not initialized"}

        stats = {
            "strategy": "collector",
            "server_id": self.server_id,
            "collector_url": self.config.collector_url,
            "initialized": self._initialized,
        }

        if self.storage:
            stats["storage"] = self.storage.get_stats()

        if self.transmission_manager:
            stats["transmission"] = {
                "last_transmission": getattr(
                    self.transmission_manager, "last_transmission", None
                ),
                "is_running": getattr(self.transmission_manager, "_running", False),
            }

        return stats

    def cleanup(self) -> None:
        """Clean up collector strategy resources."""
        logger.info("Cleaning up CollectorStrategy")

        if self.transmission_manager:
            self.transmission_manager.stop()
            self.transmission_manager = None

        if self.storage and self.config.enable_local_storage:
            # Save metrics to file before cleanup
            metrics = self.storage.get_all_metrics()
            if metrics:
                self.storage.save_to_file(metrics)
                logger.info(f"Saved {len(metrics)} metrics to file")

        self.storage = None
        self.client = None
        self._initialized = False
