"""Tests for TPS Agent main class."""

from datetime import datetime
from unittest.mock import Mock, patch

from tps_agent.agent import TPSAgent, configure_agent, record_metric
from tps_agent.config import AgentConfig
from tps_agent.models import Metric


class TestTPSAgent:
    """Test TPSAgent class."""

    def test_should_be_singleton(self):
        """TPSAgent should follow singleton pattern."""
        agent1 = TPSAgent()
        agent2 = TPSAgent()
        assert agent1 is agent2

    @patch("tps_agent.agent.HybridStorage")
    @patch("tps_agent.agent.CollectorClient")
    @patch("tps_agent.agent.TransmissionManager")
    def test_should_configure_with_config(
        self, mock_transmission, mock_client, mock_storage
    ):
        """TPSAgent should configure properly."""
        # Setup
        config = AgentConfig(
            server_id="test-server",
            collector_url="http://localhost:8080",
            enable_metrics=True,
        )

        # Mock storage
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.load_from_file.return_value = []

        # Mock client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.test_connection.return_value = True

        # Mock transmission manager
        mock_transmission_instance = Mock()
        mock_transmission.return_value = mock_transmission_instance

        # Execute
        agent = TPSAgent()
        agent.configure(config)

        # Assert
        assert agent.config == config
        assert agent.storage == mock_storage_instance
        assert agent.client == mock_client_instance
        assert agent.transmission_manager == mock_transmission_instance

        # Verify initialization calls
        mock_storage.assert_called_once()
        mock_client.assert_called_once_with(config)
        mock_transmission.assert_called_once()
        mock_transmission_instance.start.assert_called_once()

    def test_record_metric_should_store_metric(self):
        """record_metric should store metric with server_id."""
        # Setup
        agent = TPSAgent()
        mock_storage = Mock()
        mock_config = Mock()
        mock_config.server_id = "test-server"
        mock_config.enable_metrics = True

        agent.storage = mock_storage
        agent.config = mock_config

        metric = Metric(
            gateway="test_gateway",
            endpoint="test_endpoint",
            server_id="",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True,
        )

        # Execute
        agent.record_metric(metric)

        # Assert
        mock_storage.store_metric.assert_called_once()
        stored_metric = mock_storage.store_metric.call_args[0][0]
        assert stored_metric.server_id == "test-server"
        assert stored_metric.gateway == "test_gateway"

    def test_should_skip_record_when_metrics_disabled(self):
        """Should skip recording when metrics disabled."""
        # Setup
        agent = TPSAgent()
        mock_storage = Mock()
        mock_config = Mock()
        mock_config.enable_metrics = False

        agent.storage = mock_storage
        agent.config = mock_config

        metric = Metric(
            gateway="test_gateway",
            endpoint="test_endpoint",
            server_id="test-server",
            timestamp=datetime.now(),
            duration_ms=100.0,
            success=True,
        )

        # Execute
        agent.record_metric(metric)

        # Assert
        mock_storage.store_metric.assert_not_called()


class TestGlobalFunctions:
    """Test global functions."""

    @patch("tps_agent.agent.AgentConfig")
    @patch("tps_agent.agent._global_agent")
    def test_configure_agent_should_configure_global_instance(
        self, mock_agent, mock_config_class
    ):
        """configure_agent should configure the global agent."""
        # Setup
        mock_config = Mock()
        mock_config_class.from_environment.return_value = mock_config

        # Execute
        configure_agent(collector_url="http://test:8080", server_id="test-server")

        # Assert
        mock_agent.configure.assert_called_once()

        # Verify the config was created properly
        call_args = mock_agent.configure.call_args[0][0]
        assert call_args.server_id == "test-server"
        assert call_args.collector_url == "http://test:8080"

    @patch("tps_agent.agent._global_agent")
    def test_record_metric_function_should_call_agent(self, mock_agent):
        """record_metric function should call global agent."""
        # Execute
        record_metric(
            gateway="test_gateway",
            endpoint="test_endpoint",
            duration_ms=100.0,
            success=True,
        )

        # Assert
        mock_agent.record_metric.assert_called_once()

        # Verify metric structure
        metric = mock_agent.record_metric.call_args[0][0]
        assert metric.gateway == "test_gateway"
        assert metric.endpoint == "test_endpoint"
        assert metric.duration_ms == 100.0
        assert metric.success is True
