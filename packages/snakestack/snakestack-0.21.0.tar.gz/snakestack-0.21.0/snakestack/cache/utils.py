import functools
import logging
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

try:
    from redis.exceptions import RedisError
except ImportError:
    raise RuntimeError("Redis extra is not installed. Run `pip install snakestack[redis]`.")

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


def deco_cache(
    default: Any = None
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T | Any]]]:
    def decorator(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | Any]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | Any:
            try:
                return await fn(*args, **kwargs)
            except RedisError:
                logger.exception("Redis operation failed.")
                return default
        return wrapper
    return decorator
