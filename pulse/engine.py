from typing import Dict, List
import math
from pulse.models import ServiceConfig, ProbeResult, MetricSummary, ServiceState
from pulse.probes import ProbeRunner
from pulse.alerts import AlertDispatcher

class PulseMonitor:
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.history: Dict[str, List[ProbeResult]] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.current_states: Dict[str, ServiceState] = {}
        self.alert_dispatcher = AlertDispatcher()

    def register_service(self, config: ServiceConfig):
        self.services[config.id] = config
        self.history[config.id] = []
        self.consecutive_failures[config.id] = 0
        self.current_states[config.id] = ServiceState.HEALTHY

    def record_probe(self, result: ProbeResult) -> ServiceState:
        s_id = result.service_id
        config = self.services.get(s_id)
        self.history[s_id].append(result)

        if not result.is_success:
            self.consecutive_failures[s_id] += 1
        else:
            self.consecutive_failures[s_id] = 0

        thresh = config.consecutive_failures_threshold if config else 3
        failures = self.consecutive_failures[s_id]
        
        prev_state = self.current_states[s_id]
        if failures == 0:
            new_state = ServiceState.HEALTHY
        elif failures < thresh:
            new_state = ServiceState.DEGRADED
        else:
            new_state = ServiceState.OUTAGE

        if new_state != prev_state:
            self.current_states[s_id] = new_state
            self.alert_dispatcher.dispatch(s_id, new_state, result)

        return new_state

    def run_sweep(self) -> List[ProbeResult]:
        results = []
        for config in self.services.values():
            if config.probe_type == "http":
                res = ProbeRunner.execute_http_probe(config)
            else:
                res = ProbeResult(config.id, 0.0, False, None, 0.0, "Unsupported probe type")
            self.record_probe(res)
            results.append(res)
        return results

    def get_summary(self, service_id: str) -> MetricSummary:
        records = self.history.get(service_id, [])
        if not records:
            return MetricSummary(service_id, 0, 0, 100.0, 0.0, 0.0, 0.0, ServiceState.HEALTHY)

        total = len(records)
        successes = sum(1 for r in records if r.is_success)
        uptime_pct = (successes / total) * 100.0

        latencies = sorted(r.latency_ms for r in records)
        
        def percentile(p: float) -> float:
            if not latencies:
                return 0.0
            k = (len(latencies) - 1) * (p / 100.0)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return latencies[int(k)]
            d0 = latencies[int(f)] * (c - k)
            d1 = latencies[int(c)] * (k - f)
            return d0 + d1

        return MetricSummary(
            service_id=service_id,
            total_checks=total,
            success_count=successes,
            uptime_percentage=uptime_pct,
            p50_ms=percentile(50),
            p95_ms=percentile(95),
            p99_ms=percentile(99),
            current_state=self.current_states[service_id]
        )
