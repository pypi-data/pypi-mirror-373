"""Data transmission client for sending metrics to tpsCollector."""

import json
import logging
import time
from datetime import datetime
from typing import List

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import AgentConfig
from .models import HeartbeatData, Metric, MetricBatch

logger = logging.getLogger(__name__)


class TransmissionError(Exception):
    """Exception raised when metric transmission fails."""

    pass


class CollectorClient:
    """HTTP client for communicating with tpsCollector server."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.session = self._create_session()
        self.last_transmission = None

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set timeout
        session.timeout = self.config.collector_timeout

        return session

    def send_metrics(self, metrics: List[Metric]) -> bool:
        """Send metrics batch to collector. Returns True if successful."""
        if not metrics:
            return True

        batch = MetricBatch(
            server_id=self.config.server_id,
            metrics=metrics,
            batch_timestamp=datetime.now(),
        )

        try:
            url = f"{self.config.collector_url.rstrip('/')}/api/v1/metrics/batch"
            response = self.session.post(
                url, json=batch.to_dict(), headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            # Parse response
            result = response.json()
            if result.get("status") == "success":
                received_count = result.get("received_count", 0)
                logger.info(f"Successfully transmitted {received_count} metrics")
                self.last_transmission = datetime.now()
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                raise TransmissionError(f"Collector rejected metrics: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to transmit metrics: {e}")
            raise TransmissionError(f"HTTP request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse collector response: {e}")
            raise TransmissionError(f"Invalid response format: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during transmission: {e}")
            raise TransmissionError(f"Unexpected error: {e}")

    def send_heartbeat(self, heartbeat_data: HeartbeatData) -> bool:
        """Send heartbeat to collector. Returns True if successful."""
        try:
            url = f"{self.config.collector_url.rstrip('/')}/api/v1/agent/heartbeat"
            response = self.session.post(
                url,
                json=heartbeat_data.to_dict(),
                headers={"Content-Type": "application/json"},
            )

            response.raise_for_status()

            result = response.json()
            if result.get("status") == "success":
                logger.debug("Heartbeat sent successfully")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning(f"Heartbeat rejected: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            return False

    def test_connection(self) -> bool:
        """Test connection to collector. Returns True if collector is reachable."""
        try:
            url = f"{self.config.collector_url.rstrip('/')}/api/v1/health"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            result = response.json()
            return result.get("status") == "healthy"

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class TransmissionManager:
    """Manages periodic transmission of metrics with retry logic."""

    def __init__(self, config: AgentConfig, storage, client: CollectorClient):
        self.config = config
        self.storage = storage
        self.client = client
        self.is_running = False
        self._transmission_thread = None
        self._heartbeat_thread = None

    def start(self):
        """Start periodic transmission and heartbeat threads."""
        if self.is_running:
            return

        self.is_running = True

        # Start transmission thread
        import threading

        self._transmission_thread = threading.Thread(
            target=self._transmission_loop, daemon=True
        )
        self._transmission_thread.start()

        # Start heartbeat thread
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self._heartbeat_thread.start()

        logger.info("Transmission manager started")

    def stop(self):
        """Stop transmission threads."""
        self.is_running = False
        logger.info("Transmission manager stopped")

    def _transmission_loop(self):
        """Main transmission loop."""
        while self.is_running:
            try:
                # Get batch of metrics to send
                metrics = self.storage.pop_metrics(self.config.batch_size)

                if metrics:
                    success = self._send_with_retry(metrics)
                    if not success:
                        # Put metrics back if transmission failed
                        for metric in reversed(metrics):
                            self.storage.store_metric(metric)
                        logger.warning(
                            f"Failed to transmit {len(metrics)} metrics, returned to storage"
                        )

                time.sleep(self.config.transmission_interval)

            except Exception as e:
                logger.error(f"Error in transmission loop: {e}")
                time.sleep(self.config.transmission_interval)

    def _send_with_retry(self, metrics: List[Metric]) -> bool:
        """Send metrics with exponential backoff retry."""
        for attempt in range(self.config.max_retries + 1):
            try:
                return self.client.send_metrics(metrics)
            except TransmissionError as e:
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_backoff**attempt
                    logger.warning(
                        f"Transmission attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All transmission attempts failed: {e}")
                    return False

        return False

    def _heartbeat_loop(self):
        """Heartbeat transmission loop."""
        while self.is_running:
            try:
                heartbeat = HeartbeatData(
                    server_id=self.config.server_id,
                    timestamp=datetime.now(),
                    status="healthy",
                    metrics_count=self.storage.get_total_stored(),
                    local_queue_size=self.storage.get_count(),
                    last_transmission=self.client.last_transmission,
                )

                self.client.send_heartbeat(heartbeat)

                # Send heartbeat every 30 seconds
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(30)
