from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID


def safe_jsonable_encoder(obj: Any) -> Any:
    if isinstance(obj, (str, int, float, bool, type(None))):
        return str(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, (UUID, Enum, Decimal, Path)):
        return str(obj)

    if isinstance(obj, dict):
        return {safe_jsonable_encoder(k): safe_jsonable_encoder(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set, frozenset)):
        return [safe_jsonable_encoder(item) for item in obj]

    if hasattr(obj, "model_dump"):
        return safe_jsonable_encoder(obj.model_dump())

    return str(obj)
