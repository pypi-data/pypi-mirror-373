from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar, cast

try:
    from opentelemetry.trace import SpanKind
    from opentelemetry.trace.status import Status, StatusCode
except ImportError:
    raise RuntimeError("Telemetry extra is not installed. Run `pip install snakestack[telemetry]`.")

from snakestack.telemetry import get_tracer

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])

def traced_motor_method(operation_name: str) -> Callable[[F], F]:
    """
    Wrapper para criar um span em volta da operação do Motor.
    Pode ser aplicado dinamicamente nos métodos como find, insert_one etc.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer(__name__)
            collection_name = getattr(self, 'name', 'unknown_collection')

            with tracer.start_as_current_span(
                f"mongo.{operation_name}",
                kind=SpanKind.CLIENT,
            ) as span:
                span.set_attribute("db.system", "mongodb")
                db_name = getattr(getattr(self, "database", None), "name", "unknown_db")
                span.set_attribute("db.name", db_name)
                span.set_attribute("db.mongodb.collection", collection_name)
                span.set_attribute("db.operation", operation_name)

                if args:
                    span.set_attribute("db.mongo.args_count", len(args))
                if kwargs:
                    span.set_attribute("db.mongo.kwargs_keys", len(kwargs.keys()))

                try:
                    result = await func(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    span.record_exception(exc)
                    raise

        setattr(wrapper, "_is_traced_motor_method", True)
        return cast(F, wrapper)

    return decorator
