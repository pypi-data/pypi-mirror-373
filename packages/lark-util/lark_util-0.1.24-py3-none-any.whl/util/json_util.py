import json
from lark_oapi.api.bitable.v1 import AppTableRecord

import dataclasses
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import orjson


def dump_json(obj: Any) -> str:
    """用 orjson 把任意对象转成 JSON 字符串"""

    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, "__dict__"):
            return o.__dict__
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return orjson.dumps(obj, default=default, option=orjson.OPT_INDENT_2).decode(
        "utf-8"
    )
