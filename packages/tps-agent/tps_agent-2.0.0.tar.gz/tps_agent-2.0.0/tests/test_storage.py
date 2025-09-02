"""Tests for TPS Agent storage."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from tps_agent.models import Metric
from tps_agent.storage import HybridStorage, LocalStorage


class TestLocalStorage:
    """Test LocalStorage class."""

    def test_should_store_and_retrieve_metrics(self):
        """LocalStorage should store and retrieve metrics."""
        # Setup
        storage = LocalStorage(max_metrics=10)

        metric = Metric(
            gateway="test_gateway",
            endpoint="test_endpoint",
            server_id="test_server",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True,
        )

        # Execute
        storage.store_metric(metric)

        # Assert
        metrics = storage.get_metrics()
        assert len(metrics) == 1
        assert metrics[0] == metric
        assert storage.get_count() == 1
        assert storage.get_total_stored() == 1

    def test_should_pop_metrics_fifo(self):
        """LocalStorage should pop metrics in FIFO order."""
        # Setup
        storage = LocalStorage(max_metrics=10)

        metrics = []
        for i in range(3):
            metric = Metric(
                gateway=f"gateway_{i}",
                endpoint="test_endpoint",
                server_id="test_server",
                timestamp=datetime.now(),
                duration_ms=100.0,
                success=True,
            )
            metrics.append(metric)
            storage.store_metric(metric)

        # Execute
        popped = storage.pop_metrics(2)

        # Assert
        assert len(popped) == 2
        assert popped[0].gateway == "gateway_0"
        assert popped[1].gateway == "gateway_1"
        assert storage.get_count() == 1  # One remaining

    def test_should_respect_max_metrics_limit(self):
        """LocalStorage should respect max_metrics limit."""
        # Setup
        storage = LocalStorage(max_metrics=3)

        # Execute - add more metrics than limit
        for i in range(5):
            metric = Metric(
                gateway=f"gateway_{i}",
                endpoint="test_endpoint",
                server_id="test_server",
                timestamp=datetime.now(),
                duration_ms=100.0,
                success=True,
            )
            storage.store_metric(metric)

        # Assert
        assert storage.get_count() == 3  # Limited to max
        assert storage.get_total_stored() == 5  # But total count tracks all

    def test_should_clean_old_metrics(self):
        """LocalStorage should clean old metrics based on retention."""
        # Setup
        storage = LocalStorage(retention_minutes=1)  # 1 minute retention

        # Add old metric
        old_metric = Metric(
            gateway="old_gateway",
            endpoint="test_endpoint",
            server_id="test_server",
            timestamp=datetime.now() - timedelta(minutes=2),  # 2 minutes old
            duration_ms=100.0,
            success=True,
        )
        storage.store_metric(old_metric)

        # Add new metric
        new_metric = Metric(
            gateway="new_gateway",
            endpoint="test_endpoint",
            server_id="test_server",
            timestamp=datetime.now(),  # Current time
            duration_ms=100.0,
            success=True,
        )
        storage.store_metric(new_metric)

        # Execute
        removed_count = storage.clear_old_metrics()

        # Assert
        assert removed_count == 1
        assert storage.get_count() == 1
        remaining = storage.get_metrics()
        assert remaining[0].gateway == "new_gateway"


class TestHybridStorage:
    """Test HybridStorage class."""

    @patch("tps_agent.storage.FileStorage")
    @patch("tps_agent.storage.LocalStorage")
    def test_should_initialize_with_components(
        self, mock_local_storage, mock_file_storage
    ):
        """HybridStorage should initialize with memory and file storage."""
        # Setup
        mock_local_instance = Mock()
        mock_local_storage.return_value = mock_local_instance
        mock_file_instance = Mock()
        mock_file_storage.return_value = mock_file_instance

        # Execute
        storage = HybridStorage(max_metrics=100, enable_file_storage=True)

        # Assert
        assert storage.memory_storage == mock_local_instance
        assert storage.file_storage == mock_file_instance
        mock_local_storage.assert_called_once_with(100, 10)  # default retention
        mock_file_storage.assert_called_once_with(None)  # default file path

    @patch("tps_agent.storage.FileStorage")
    @patch("tps_agent.storage.LocalStorage")
    def test_should_store_metric_in_memory(self, mock_local_storage, mock_file_storage):
        """HybridStorage should store metrics in memory storage."""
        # Setup
        mock_local_instance = Mock()
        mock_local_storage.return_value = mock_local_instance
        storage = HybridStorage()

        metric = Metric(
            gateway="test_gateway",
            endpoint="test_endpoint",
            server_id="test_server",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True,
        )

        # Execute
        storage.store_metric(metric)

        # Assert
        mock_local_instance.store_metric.assert_called_once_with(metric)

    def test_should_disable_file_storage_when_requested(self):
        """HybridStorage should disable file storage when requested."""
        # Execute
        storage = HybridStorage(enable_file_storage=False)

        # Assert
        assert storage.file_storage is None
