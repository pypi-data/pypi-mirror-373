from typing import Any, Self, cast

import orjson

try:
    from redis.asyncio import Redis
except ImportError:
    raise RuntimeError("Redis extra is not installed. Run `pip install snakestack[redis]`.")
from snakestack.cache.utils import deco_cache
from snakestack.logging.encoders import safe_jsonable_encoder


class AsyncRedisService:
    """
    Serviço assíncrono para operações básicas com Redis,
    com suporte a prefixo de chave, TTL padrão e serialização JSON.
    """

    def __init__(
        self: Self,
        client: Redis,
        default_ttl: int | None = None,
        prefix: str = "",
    ) -> None:
        """
        Inicializa o serviço Redis.

        Args:
            client: Instância de redis.asyncio.Redis já conectada.
            default_ttl: Tempo padrão de expiração em segundos (opcional).
            prefix: Prefixo opcional para organizar as chaves.
        """
        self._client = client
        self._default_ttl = default_ttl
        self._prefix = prefix.strip(":")

    def _format_key(self: Self, key: str) -> str:
        """Adiciona o prefixo à chave, se configurado."""
        return f"{self._prefix}:{key}" if self._prefix else key

    @deco_cache(default=False)
    async def set(self: Self, key: str, value: Any, ex: int | None = None) -> bool:
        """
        Armazena um valor serializado em Redis com TTL opcional.

        Args:
           key: Nome da chave.
           value: Valor a ser serializado.
           ex: Expiração em segundos (override do TTL padrão).

        Returns:
           True se armazenado com sucesso, False em caso de erro.
        """
        serialized = orjson.dumps(value, default=safe_jsonable_encoder)
        return bool(await self._client.set(
            name=self._format_key(key),
            value=serialized,
            ex=ex or self._default_ttl,
        ))

    @deco_cache(default=None)
    async def get(self: Self, key: str) -> Any | None:
        """
        Recupera e desserializa um valor armazenado em Redis.

        Args:
            key: Nome da chave.

        Returns:
            Valor desserializado ou None.
        """
        raw = await self._client.get(self._format_key(key))
        if raw is None:
            return None
        try:
            return orjson.loads(raw)
        except orjson.JSONDecodeError:
            return raw

    @deco_cache(default=0)
    async def delete(self: Self, key: str) -> int:
        """Remove uma chave do Redis. Retorna 1 se removida, 0 se não existe."""
        result = await self._client.delete(self._format_key(key))
        return cast(int, result)

    @deco_cache(default=False)
    async def exists(self: Self, key: str) -> bool:
        """Verifica se a chave existe em Redis."""
        return bool(await self._client.exists(self._format_key(key)))

    @deco_cache(default=False)
    async def expire(self: Self, key: str, ttl: int) -> bool:
        """Define um tempo de expiração (em segundos) para uma chave."""
        return bool(await self._client.expire(self._format_key(key), ttl))

    @deco_cache(default=0)
    async def incr(self: Self, key: str, amount: int = 1) -> int:
        """Incrementa um valor numérico armazenado na chave."""
        result = await self._client.incr(self._format_key(key), amount)
        return cast(int, result)

    @deco_cache(default=0)
    async def decr(self: Self, key: str, amount: int = 1) -> int:
        """Decrementa um valor numérico armazenado na chave."""
        result = await self._client.decr(self._format_key(key), amount)
        return cast(int, result)

    @deco_cache(default=0)
    async def ttl(self: Self, key: str) -> int:
        """Obtém o tempo de expiração restante da chave, em segundos."""
        result = await self._client.ttl(self._format_key(key))
        return cast(int, result)

    @deco_cache(default=False)
    async def ping(self) -> bool:
        result = await self._client.ping()
        return cast(bool, result)
