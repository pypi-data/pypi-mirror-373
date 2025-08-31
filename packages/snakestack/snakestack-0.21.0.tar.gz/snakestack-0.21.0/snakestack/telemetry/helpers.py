import functools
import inspect
from typing import Awaitable, Callable, ParamSpec, TypeVar, cast

try:
    from opentelemetry import trace
except ImportError:
    raise RuntimeError("Telemetry extra is not installed. Run `pip install snakestack[telemetry]`.")


_T = TypeVar("_T")
_P = ParamSpec("_P")


def get_current_span() -> trace.Span:
    return trace.get_current_span()


def get_tracer(name: str, version: str = "1.0.0") -> trace.Tracer:
    """Obtém o tracer padrão da aplicação."""
    return trace.get_tracer(name, version)


def instrumented_span(
    span_name: str
) -> Callable[[Callable[_P, _T] | Callable[_P, Awaitable[_T]]], Callable[_P, _T] | Callable[_P, Awaitable[_T]]]:
    """Decorator that creates a span with the given name for sync or async functions."""

    def decorator(
        func: Callable[_P, _T] | Callable[_P, Awaitable[_T]]
    ) -> Callable[_P, _T] | Callable[_P, Awaitable[_T]]:
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                with get_tracer(func.__module__).start_as_current_span(span_name):
                    return await cast(Callable[_P, Awaitable[_T]], func)(*args, **kwargs)
            return cast(Callable[_P, Awaitable[_T]], async_wrapper)

        else:
            @functools.wraps(func)
            def sync_wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                with get_tracer(func.__module__).start_as_current_span(span_name):
                    return cast(Callable[_P, _T], func)(*args, **kwargs)
            return cast(Callable[_P, _T], sync_wrapper)

    return decorator


def set_span_attributes(**attrs: str | int | float | bool) -> None:
    span = get_current_span()
    for key, value in attrs.items():
        span.set_attribute(key, value)
