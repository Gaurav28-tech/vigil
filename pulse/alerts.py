import time
from typing import Dict
from pulse.models import ServiceState, ProbeResult

class AlertDispatcher:
    def __init__(self, cooldown_seconds: float = 300.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time: Dict[str, float] = {}
        self.alert_history = []

    def dispatch(self, service_id: str, new_state: ServiceState, result: ProbeResult):
        now = time.time()
        last = self.last_alert_time.get(service_id, 0.0)
        if (now - last) < self.cooldown_seconds and new_state != ServiceState.HEALTHY:
            return  # Suppress alert due to cooldown
        
        self.last_alert_time[service_id] = now
        payload = {
            "service_id": service_id,
            "state": new_state.value,
            "latency_ms": result.latency_ms,
            "timestamp": now,
            "error": result.error_message
        }
        self.alert_history.append(payload)
        # In production, this can send to webhook or Slack
