import logging
from typing import Any

try:
    from motor.motor_asyncio import (
        AsyncIOMotorClient,
        AsyncIOMotorCollection,
        AsyncIOMotorDatabase,
    )
    from pymongo.errors import PyMongoError
except ImportError:
    raise RuntimeError("Mongodb extra is not installed. Run `pip install snakestack[mongodb]`.")


class DB:
    client: AsyncIOMotorClient[Any] | None = None

db = DB()

logger = logging.getLogger(__name__)


async def open_mongodb_connection(
    host: str
) -> None:
    logger.debug("Connecting to mongodb...")
    if not host.startswith("mongodb"):
        raise ValueError("Invalid MongoDB URL configured.")
    db.client = AsyncIOMotorClient(host)
    logger.debug("Connecting to mongodb successful.")


async def close_mongodb_connection() -> None:
    logger.debug("Closing connection with mongodb...")
    if db.client:
        db.client.close()
    logger.debug("Connection with mongodb is closed.")


def get_collection(dbname: str, collection: str) -> AsyncIOMotorCollection[Any]:
    if not db.client:
        raise RuntimeError("Connection with mongodb is not starting.")
    return db.client[dbname][collection]


def get_database(dbname: str) -> AsyncIOMotorDatabase[Any]:
    if not db.client:
        raise RuntimeError("Connection with mongodb is not starting.")
    return db.client[dbname]


async def ping() -> bool:
    if not db.client:
        raise RuntimeError("Connection with mongodb is not starting.")
    try:
        await db.client.admin.command("ping")
        return True
    except PyMongoError:
        return False
