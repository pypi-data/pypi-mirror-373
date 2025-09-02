"""Configuration for TPS Agent."""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for TPS Agent."""

    # Server identification
    server_id: str

    # Collector connection
    collector_url: str
    collector_timeout: int = 30

    # Local storage settings
    max_local_metrics: int = 10000
    batch_size: int = 100

    # Transmission settings
    transmission_interval: int = 60  # seconds
    max_retries: int = 3
    retry_backoff: float = 1.0  # exponential backoff multiplier

    # Local cleanup
    local_retention_minutes: int = 10

    # Feature toggles
    enable_metrics: bool = True
    enable_throttling: bool = True
    enable_local_storage: bool = True

    # Grafana integration
    monitoring_mode: str = "collector"  # collector, grafana, both
    prometheus_port: int = 8000

    @classmethod
    def from_environment(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        return cls(
            server_id=os.getenv("TPS_SERVER_ID", "unknown"),
            collector_url=os.getenv("TPS_COLLECTOR_URL", "http://localhost:8080"),
            collector_timeout=int(os.getenv("TPS_COLLECTOR_TIMEOUT", "30")),
            max_local_metrics=int(os.getenv("TPS_MAX_LOCAL_METRICS", "10000")),
            batch_size=int(os.getenv("TPS_BATCH_SIZE", "100")),
            transmission_interval=int(os.getenv("TPS_TRANSMISSION_INTERVAL", "60")),
            max_retries=int(os.getenv("TPS_MAX_RETRIES", "3")),
            retry_backoff=float(os.getenv("TPS_RETRY_BACKOFF", "1.0")),
            local_retention_minutes=int(os.getenv("TPS_LOCAL_RETENTION_MINUTES", "10")),
            enable_metrics=os.getenv("TPS_ENABLE_METRICS", "true").lower() == "true",
            enable_throttling=os.getenv("TPS_ENABLE_THROTTLING", "true").lower()
            == "true",
            enable_local_storage=os.getenv("TPS_ENABLE_LOCAL_STORAGE", "true").lower()
            == "true",
            monitoring_mode=os.getenv("TPS_MONITORING_MODE", "collector"),
            prometheus_port=int(os.getenv("TPS_PROMETHEUS_PORT", "8000")),
        )
