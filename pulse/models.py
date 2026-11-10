from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import time

class ServiceState(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    OUTAGE = "OUTAGE"

@dataclass
class ServiceConfig:
    id: str
    name: str
    target: str
    probe_type: str = "http"
    interval_seconds: int = 15
    timeout_seconds: float = 3.0
    expected_status: int = 200
    consecutive_failures_threshold: int = 3

@dataclass
class ProbeResult:
    service_id: str
    timestamp: float
    is_success: bool
    status_code: Optional[int]
    latency_ms: float
    error_message: Optional[str] = None

@dataclass
class MetricSummary:
    service_id: str
    total_checks: int
    success_count: int
    uptime_percentage: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    current_state: ServiceState
