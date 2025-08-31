from typing import Any

try:
    from redis.asyncio import Redis
except ImportError:
    raise RuntimeError("Redis extra is not installed. Run `pip install snakestack[redis]`.")

def create_async_redis_client(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    username: str | None = None,
    password: str | None = None,
    decode_responses: bool = True,
    **kwargs: Any,
) -> Redis:
    redis = Redis(
        host=host,
        port=port,
        db=db,
        username=username,
        password=password,
        decode_responses=decode_responses,
        **kwargs,
    )
    return redis
