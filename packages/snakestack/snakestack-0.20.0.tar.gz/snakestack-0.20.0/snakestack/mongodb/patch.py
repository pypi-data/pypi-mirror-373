import logging
from typing import Any, Callable

try:
    from motor.motor_asyncio import AsyncIOMotorCollection
except ImportError:
    raise RuntimeError("Mongodb extra is not installed. Run `pip install snakestack[mongodb]`.")

from snakestack.mongodb.tracing import traced_motor_method

logger = logging.getLogger(__name__)


def patch_motor_collection_methods() -> None:
    methods_to_patch = [
        "find",
        "find_one",
        "insert_one",
        "insert_many",
        "update_one",
        "update_many",
        "delete_one",
        "delete_many",
        "replace_one",
        "aggregate",
    ]

    for method_name in methods_to_patch:
        if hasattr(AsyncIOMotorCollection, method_name):
            original = getattr(AsyncIOMotorCollection, method_name)
            patched = traced_motor_method(method_name)(original)
            if not is_already_patched(original):
                logger.debug("MongoDB collection method '%s' patched for tracing.", method_name)
                setattr(AsyncIOMotorCollection, method_name, patched)


def is_already_patched(method: Callable[..., Any]) -> bool:
    return getattr(method, "_is_traced_motor_method", False)
