# Pulse Monitor 📡

[![CI](https://github.com/Gaurav28-tech/pulse-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/Gaurav28-tech/pulse-monitor)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-brightgreen.svg)]()

**Pulse Monitor** is a lightweight synthetic service health and latency telemetry engine designed for microservices and cloud workloads. It conducts periodic synthetic HTTP/TCP probes, tracks latency distributions (p50, p95, p99), triggers incident workflows, and dispatches alerts with cooldown suppression.

---

## 🚀 Key Features

- **Synthetic Probes**: Automated HTTP and TCP health probes with custom headers, expected status codes, and assertion validations.
- **Latency Telemetry**: Real-time percentiles calculation (p50, p95, p99) and moving window uptime percentage.
- **Incident Lifecycle**: Automatic state transition from `HEALTHY` ➔ `DEGRADED` ➔ `OUTAGE` with configurable consecutive failure thresholds.
- **Smart Alerting**: Webhook & console dispatchers equipped with intelligent cooldown timers to eliminate notification fatigue.
- **Zero Heavy Dependencies**: Built with Python standard library modules for minimal overhead and instant deployment.

---

## 🏗️ Architecture

```
+--------------------------------------------------------+
|                      Pulse Engine                      |
+--------------------------------------------------------+
           |                                  |
    [Synthetic Probe]                  [Telemetry Calc]
           |                                  |
           v                                  v
+-----------------------+          +---------------------+
| Target Endpoint / API |          | Latency Percentiles |
| (HTTP/TCP Response)   |          | (p50, p95, p99)     |
+-----------------------+          +---------------------+
           |                                  |
           +-----------------+----------------+
                             |
                             v
                  [State Machine & Alert]
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
         (Console Dispatch)      (Webhook Payload)
```

---

## 📦 Quickstart

### Installation

Clone the repository:
```bash
git clone https://github.com/Gaurav28-tech/pulse-monitor.git
cd pulse-monitor
```

### Basic Usage

```python
from pulse.engine import PulseMonitor
from pulse.models import ServiceConfig

monitor = PulseMonitor()

# Register a service target
monitor.register_service(
    ServiceConfig(
        id="payment-service",
        name="Stripe Payment Gateway",
        target="https://api.stripe.com/healthcheck",
        probe_type="http",
        interval_seconds=10,
        expected_status=200
    )
)

# Run a synthetic probe sweep
results = monitor.run_sweep()
for res in results:
    print(f"Service: {res.service_id} | Status: {res.status} | Latency: {res.latency_ms:.2f}ms")
```

### Running the Test Suite

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
