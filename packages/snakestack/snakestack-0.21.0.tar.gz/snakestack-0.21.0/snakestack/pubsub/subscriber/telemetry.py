from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar, cast

try:
    from opentelemetry.trace import SpanKind, StatusCode
except ImportError:
    raise RuntimeError("Telemetry extra is not installed. Run `pip install snakestack[telemetry]`.")

from snakestack.telemetry import get_tracer

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])
tracer = get_tracer("snakestack.pubsub.processor")

def traced_processor(operation_name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(operation_name, kind=SpanKind.INTERNAL) as span:
                try:
                    if "message" in kwargs:
                        span.set_attribute("message.id", kwargs["message"].message_id)
                    if "items" in kwargs:
                        span.set_attribute("batch.size", len(kwargs["items"]))
                    return await func(*args, **kwargs)
                except Exception as e:
                    span.set_status(StatusCode.ERROR)
                    span.record_exception(e)
                    raise

        return cast(F, wrapper)
    return decorator
