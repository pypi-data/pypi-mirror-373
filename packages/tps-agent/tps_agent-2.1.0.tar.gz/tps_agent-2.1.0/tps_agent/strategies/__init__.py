"""
TPS Agent Monitoring Strategies.

This module provides different monitoring strategies that can be used independently:
- CollectorStrategy: TPS Agent -> TPS Collector -> Dashboard
- PrometheusStrategy: TPS Agent -> Prometheus -> Grafana
- HybridStrategy: TPS Agent -> TPS Collector -> Grafana
- PostgreSQLStrategy: TPS Agent -> PostgreSQL -> Grafana (Direct)
"""

from .base import MonitoringStrategy
from .collector_strategy import CollectorStrategy
from .hybrid_strategy import HybridStrategy
from .postgresql_strategy import PostgreSQLStrategy
from .prometheus_strategy import PrometheusStrategy

__all__ = [
    "MonitoringStrategy",
    "CollectorStrategy",
    "PrometheusStrategy",
    "HybridStrategy",
    "PostgreSQLStrategy",
]
