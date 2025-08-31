import inspect
import logging
import socket
import time
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable, Self

from .model import CheckModel, HealthCheckModel

logger = logging.getLogger(__name__)

class SnakeHealthCheck:

    UPTIME_DIR = "/proc/uptime"

    def __init__(
        self: Self,
        service_name: str,
        service_version: str,
        service_environment: str,
    ) -> None:
        self._checks: dict[str, Callable[[], bool | Awaitable[bool]]] = {}
        self._service_name = service_name
        self._service_version = service_version
        self._service_environment = service_environment

    async def is_healthy(self: Self) -> tuple[dict[str, Any], bool]:
        result = {}
        timestamp = datetime.now(UTC).isoformat()
        uptime = self._uptime()

        checks: list[bool] = list()
        for name, check_fn in self._checks.items():
            start_check = time.perf_counter()
            ok, error = await self._safe_call(fn=check_fn)
            latency = round((time.perf_counter() - start_check) * 1000, 2)

            result[name] = CheckModel(
                ok=ok,
                latency_ms=latency,
                error=error if error else None
            ).model_dump()
            checks.append(ok)

        all_ok = all(checks)

        total_latency = sum(dep["latency_ms"] for dep in result.values())
        data = {
            "service_name": self._service_name,
            "version": self._service_version,
            "environment": self._service_environment,
            "host": socket.gethostname(),
            "timestamp": timestamp,
            "uptime": uptime,
            "status": all_ok,
            "latency_ms": total_latency,
            "details": result,
        }
        model = HealthCheckModel(**data).model_dump(exclude_none=True)
        return model, all_ok

    async def _safe_call(
        self: Self, fn: Callable[[], bool | Awaitable[bool]]
    ) -> tuple[bool, Any]:
        try:
            if inspect.iscoroutinefunction(fn):
                result = await fn()
            else:
                result = fn()
            return bool(result), None
        except Exception as error:
            logger.exception("Error on health check function", exc_info=error)
            return False, str(error)

    def add_check(self: Self, name: str, func: Callable[[], bool | Awaitable[bool]]) -> None:
        if name not in self._checks:
            self._checks[name] = func

    def _uptime(self: Self) -> str | None:
        try:
            with open(self.UPTIME_DIR) as f:
                uptime_seconds = float(f.readline().split()[0])
                hours, remainder = divmod(int(uptime_seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{hours}h {minutes}m {seconds}s"
        except Exception:
            return None
