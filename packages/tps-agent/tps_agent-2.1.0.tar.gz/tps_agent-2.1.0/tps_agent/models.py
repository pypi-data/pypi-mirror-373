"""Data models for TPS Agent."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Metric:
    """Represents a single TPS measurement."""

    gateway: str
    endpoint: str
    server_id: str
    timestamp: datetime
    duration_ms: float
    success: bool
    error: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metric":
        """Create Metric from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class MetricBatch:
    """Represents a batch of metrics for transmission."""

    server_id: str
    metrics: list[Metric]
    batch_timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "server_id": self.server_id,
            "metrics": [m.to_dict() for m in self.metrics],
            "batch_timestamp": self.batch_timestamp.isoformat(),
        }


@dataclass
class HeartbeatData:
    """Represents agent heartbeat data."""

    server_id: str
    timestamp: datetime
    status: str = "healthy"
    metrics_count: int = 0
    local_queue_size: int = 0
    last_transmission: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "server_id": self.server_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "metrics_count": self.metrics_count,
            "local_queue_size": self.local_queue_size,
            "last_transmission": (
                self.last_transmission.isoformat() if self.last_transmission else None
            ),
        }
