import time
import urllib.request
import urllib.error
import socket
from pulse.models import ServiceConfig, ProbeResult

class ProbeRunner:
    @staticmethod
    def execute_http_probe(config: ServiceConfig) -> ProbeResult:
        start_time = time.perf_counter()
        req = urllib.request.Request(
            config.target,
            headers={"User-Agent": "PulseMonitor/0.1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
                elapsed = (time.perf_counter() - start_time) * 1000.0
                status = resp.getcode()
                is_success = (status == config.expected_status)
                return ProbeResult(
                    service_id=config.id,
                    timestamp=time.time(),
                    is_success=is_success,
                    status_code=status,
                    latency_ms=elapsed,
                    error_message=None if is_success else f"Expected {config.expected_status}, got {status}"
                )
        except urllib.error.HTTPError as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ProbeResult(
                service_id=config.id,
                timestamp=time.time(),
                is_success=(e.code == config.expected_status),
                status_code=e.code,
                latency_ms=elapsed,
                error_message=str(e)
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ProbeResult(
                service_id=config.id,
                timestamp=time.time(),
                is_success=False,
                status_code=None,
                latency_ms=elapsed,
                error_message=str(e)
            )

    @staticmethod
    def execute_tcp_probe(config: ServiceConfig, host: str, port: int) -> ProbeResult:
        start_time = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=config.timeout_seconds):
                elapsed = (time.perf_counter() - start_time) * 1000.0
                return ProbeResult(
                    service_id=config.id,
                    timestamp=time.time(),
                    is_success=True,
                    status_code=None,
                    latency_ms=elapsed
                )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ProbeResult(
                service_id=config.id,
                timestamp=time.time(),
                is_success=False,
                status_code=None,
                latency_ms=elapsed,
                error_message=str(e)
            )
