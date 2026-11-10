import unittest
from unittest.mock import patch, MagicMock
from pulse.models import ServiceConfig, ProbeResult, ServiceState
from pulse.engine import PulseMonitor

class TestPulseMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PulseMonitor()
        self.config = ServiceConfig(
            id="auth-svc",
            name="Authentication Service",
            target="https://auth.internal/health",
            consecutive_failures_threshold=3
        )
        self.monitor.register_service(self.config)

    def test_state_transitions(self):
        # 1 success -> HEALTHY
        state1 = self.monitor.record_probe(ProbeResult("auth-svc", 100.0, True, 200, 15.0))
        self.assertEqual(state1, ServiceState.HEALTHY)

        # 1 failure -> DEGRADED (< threshold of 3)
        state2 = self.monitor.record_probe(ProbeResult("auth-svc", 101.0, False, 500, 20.0))
        self.assertEqual(state2, ServiceState.DEGRADED)

        # 2nd failure -> DEGRADED
        state3 = self.monitor.record_probe(ProbeResult("auth-svc", 102.0, False, 500, 20.0))
        self.assertEqual(state3, ServiceState.DEGRADED)

        # 3rd failure -> OUTAGE (reaches threshold)
        state4 = self.monitor.record_probe(ProbeResult("auth-svc", 103.0, False, 500, 20.0))
        self.assertEqual(state4, ServiceState.OUTAGE)

        # Recovery -> HEALTHY
        state5 = self.monitor.record_probe(ProbeResult("auth-svc", 104.0, True, 200, 12.0))
        self.assertEqual(state5, ServiceState.HEALTHY)

    def test_metrics_percentiles(self):
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        for lat in latencies:
            self.monitor.record_probe(ProbeResult("auth-svc", 100.0, True, 200, lat))

        summary = self.monitor.get_summary("auth-svc")
        self.assertEqual(summary.total_checks, 10)
        self.assertEqual(summary.success_count, 10)
        self.assertEqual(summary.uptime_percentage, 100.0)
        self.assertAlmostEqual(summary.p50_ms, 55.0, delta=1.0)
        self.assertTrue(summary.p95_ms > 85.0)

    def test_alert_suppression_cooldown(self):
        self.monitor.record_probe(ProbeResult("auth-svc", 100.0, False, 500, 20.0))
        initial_alerts = len(self.monitor.alert_dispatcher.alert_history)
        self.assertEqual(initial_alerts, 1)

        # Trigger another failure immediately (within cooldown)
        self.monitor.record_probe(ProbeResult("auth-svc", 101.0, False, 500, 20.0))
        # Alert count should remain 1 because state remained DEGRADED and within cooldown
        self.assertEqual(len(self.monitor.alert_dispatcher.alert_history), 1)

if __name__ == "__main__":
    unittest.main()
