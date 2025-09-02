"""Tests for TPS Agent decorators."""

from unittest.mock import Mock, patch

import pytest

from tps_agent.decorators import ThrottleException, measure_tps, throttle


class TestMeasureTpsDecorator:
    """Test measure_tps decorator."""

    @patch("tps_agent.decorators.get_agent")
    @patch("tps_agent.decorators.record_metric")
    def test_should_measure_sync_function_execution(self, mock_record, mock_get_agent):
        """measure_tps should record metrics for sync functions."""
        # Setup
        mock_agent = Mock()
        mock_agent.config = Mock()
        mock_agent.config.enable_metrics = True
        mock_get_agent.return_value = mock_agent

        @measure_tps(gateway="test_gateway", endpoint="test_endpoint")
        def test_function():
            return "test_result"

        # Execute
        result = test_function()

        # Assert
        assert result == "test_result"
        mock_record.assert_called_once()

        # Verify metric call arguments
        call_args = mock_record.call_args
        assert call_args.kwargs["gateway"] == "test_gateway"
        assert call_args.kwargs["endpoint"] == "test_endpoint"
        assert call_args.kwargs["success"] is True
        assert call_args.kwargs["error"] is None

    @pytest.mark.asyncio
    @patch("tps_agent.decorators.get_agent")
    @patch("tps_agent.decorators.record_metric")
    async def test_should_measure_async_function_execution(
        self, mock_record, mock_get_agent
    ):
        """measure_tps should record metrics for async functions."""
        # Setup
        mock_agent = Mock()
        mock_agent.config = Mock()
        mock_agent.config.enable_metrics = True
        mock_get_agent.return_value = mock_agent

        @measure_tps(gateway="test_gateway", endpoint="test_endpoint")
        async def test_async_function():
            return "async_result"

        # Execute
        result = await test_async_function()

        # Assert
        assert result == "async_result"
        mock_record.assert_called_once()

    @patch("tps_agent.decorators.get_agent")
    def test_should_skip_metrics_when_disabled(self, mock_get_agent):
        """measure_tps should skip metrics when disabled."""
        # Setup
        mock_agent = Mock()
        mock_agent.config = None
        mock_get_agent.return_value = mock_agent

        @measure_tps(gateway="test_gateway")
        def test_function():
            return "result"

        # Execute
        result = test_function()

        # Assert
        assert result == "result"
        # No metrics should be recorded


class TestThrottleDecorator:
    """Test throttle decorator."""

    @patch("tps_agent.decorators.get_agent")
    @patch("tps_agent.decorators._throttler")
    def test_should_allow_execution_when_throttle_passes(
        self, mock_throttler, mock_get_agent
    ):
        """throttle should allow execution when rate limit not exceeded."""
        # Setup
        mock_agent = Mock()
        mock_agent.config = Mock()
        mock_agent.config.enable_throttling = True
        mock_get_agent.return_value = mock_agent
        mock_throttler.check_rate_limit.return_value = True

        @throttle(gateway="test_gateway", max_tps=10)
        def test_function():
            return "allowed"

        # Execute
        result = test_function()

        # Assert
        assert result == "allowed"
        mock_throttler.check_rate_limit.assert_called_once_with("test_gateway", 10, 1)

    @patch("tps_agent.decorators.get_agent")
    @patch("tps_agent.decorators._throttler")
    def test_should_raise_throttle_exception_when_rate_limit_exceeded(
        self, mock_throttler, mock_get_agent
    ):
        """throttle should raise ThrottleException when rate limit exceeded."""
        # Setup
        mock_agent = Mock()
        mock_agent.config = Mock()
        mock_agent.config.enable_throttling = True
        mock_get_agent.return_value = mock_agent
        mock_throttler.check_rate_limit.return_value = False
        mock_throttler.get_current_tps.return_value = 15.0

        @throttle(gateway="test_gateway", max_tps=10)
        def test_function():
            return "should_not_execute"

        # Execute & Assert
        with pytest.raises(ThrottleException) as exc_info:
            test_function()

        assert exc_info.value.gateway == "test_gateway"
        assert exc_info.value.max_tps == 10
        assert exc_info.value.current_tps == 15.0
