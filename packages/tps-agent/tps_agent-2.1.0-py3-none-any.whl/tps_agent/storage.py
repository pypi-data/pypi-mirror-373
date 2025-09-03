"""Local storage for TPS Agent metrics."""

import json
import logging
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .models import Metric

logger = logging.getLogger(__name__)


class LocalStorage:
    """Thread-safe local storage for metrics with automatic cleanup."""

    def __init__(self, max_metrics: int = 10000, retention_minutes: int = 10):
        self.max_metrics = max_metrics
        self.retention_minutes = retention_minutes
        self._metrics = deque(maxlen=max_metrics)
        self._lock = threading.Lock()
        self._total_stored = 0

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def store_metric(self, metric: Metric) -> None:
        """Store a single metric."""
        with self._lock:
            self._metrics.append(metric)
            self._total_stored += 1

    def get_metrics(self, limit: Optional[int] = None) -> List[Metric]:
        """Get metrics, optionally limited to a certain count."""
        with self._lock:
            if limit is None:
                return list(self._metrics)
            return list(self._metrics)[:limit]

    def pop_metrics(self, count: int) -> List[Metric]:
        """Pop (remove and return) metrics from the front of the queue."""
        with self._lock:
            result = []
            for _ in range(min(count, len(self._metrics))):
                if self._metrics:
                    result.append(self._metrics.popleft())
            return result

    def get_count(self) -> int:
        """Get current number of stored metrics."""
        with self._lock:
            return len(self._metrics)

    def get_total_stored(self) -> int:
        """Get total number of metrics stored since startup."""
        return self._total_stored

    def clear_old_metrics(self) -> int:
        """Remove metrics older than retention period. Returns count removed."""
        cutoff_time = datetime.now() - timedelta(minutes=self.retention_minutes)
        removed_count = 0

        with self._lock:
            # Remove old metrics from front of deque
            while self._metrics and self._metrics[0].timestamp < cutoff_time:
                self._metrics.popleft()
                removed_count += 1

        return removed_count

    def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                removed = self.clear_old_metrics()
                if removed > 0:
                    logger.debug(f"Cleaned up {removed} old metrics")
                time.sleep(60)  # Run cleanup every minute
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60)


class FileStorage:
    """File-based storage for metrics persistence across restarts."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = Path(file_path or "tps_agent_metrics.json")
        self._lock = threading.Lock()

    def save_metrics(self, metrics: List[Metric]) -> None:
        """Save metrics to file."""
        with self._lock:
            try:
                data = [m.to_dict() for m in metrics]
                with open(self.file_path, "w") as f:
                    json.dump(data, f, indent=2)
                logger.debug(f"Saved {len(metrics)} metrics to {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to save metrics to file: {e}")

    def load_metrics(self) -> List[Metric]:
        """Load metrics from file."""
        with self._lock:
            try:
                if not self.file_path.exists():
                    return []

                with open(self.file_path, "r") as f:
                    data = json.load(f)

                metrics = [Metric.from_dict(item) for item in data]
                logger.debug(f"Loaded {len(metrics)} metrics from {self.file_path}")
                return metrics

            except Exception as e:
                logger.error(f"Failed to load metrics from file: {e}")
                return []

    def clear_file(self) -> None:
        """Clear the metrics file."""
        with self._lock:
            try:
                if self.file_path.exists():
                    self.file_path.unlink()
                    logger.debug("Cleared metrics file")
            except Exception as e:
                logger.error(f"Failed to clear metrics file: {e}")


class HybridStorage:
    """Combines memory and file storage for reliability."""

    def __init__(
        self,
        max_metrics: int = 10000,
        retention_minutes: int = 10,
        enable_file_storage: bool = True,
        file_path: Optional[str] = None,
    ):
        self.memory_storage = LocalStorage(max_metrics, retention_minutes)
        self.file_storage = FileStorage(file_path) if enable_file_storage else None
        self._last_file_save = time.time()
        self._file_save_interval = 300  # Save to file every 5 minutes

    def store_metric(self, metric: Metric) -> None:
        """Store metric in memory and periodically to file."""
        self.memory_storage.store_metric(metric)

        # Periodically save to file
        if (
            self.file_storage
            and time.time() - self._last_file_save > self._file_save_interval
        ):
            self._save_to_file()

    def get_metrics(self, limit: Optional[int] = None) -> List[Metric]:
        """Get metrics from memory storage."""
        return self.memory_storage.get_metrics(limit)

    def pop_metrics(self, count: int) -> List[Metric]:
        """Pop metrics from memory storage."""
        return self.memory_storage.pop_metrics(count)

    def get_count(self) -> int:
        """Get current metrics count."""
        return self.memory_storage.get_count()

    def get_total_stored(self) -> int:
        """Get total metrics stored."""
        return self.memory_storage.get_total_stored()

    def _save_to_file(self) -> None:
        """Save current metrics to file."""
        if self.file_storage:
            metrics = self.memory_storage.get_metrics()
            self.file_storage.save_metrics(metrics)
            self._last_file_save = time.time()

    def load_from_file(self) -> List[Metric]:
        """Load metrics from file (typically on startup)."""
        if self.file_storage:
            return self.file_storage.load_metrics()
        return []

    def clear_file(self) -> None:
        """Clear file storage."""
        if self.file_storage:
            self.file_storage.clear_file()
