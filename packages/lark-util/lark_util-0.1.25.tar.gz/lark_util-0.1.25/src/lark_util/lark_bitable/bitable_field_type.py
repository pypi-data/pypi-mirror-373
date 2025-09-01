from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List
from datetime import datetime


class BaseBitableFieldType(ABC):
    @abstractmethod
    def escape_out(self, value: Any) -> Any:
        pass

    @abstractmethod
    def escape_in(self, value: Any) -> Any:
        pass


class TextBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise ValueError(
            f"TextBitableFieldType escape_out value must be str, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            if len(value) > 0:
                for item in value:
                    if isinstance(item, dict) and "text" in item:
                        return item.get("text", None)
            return None
        raise ValueError(
            f"TextBitableFieldType escape_in value must be str or list, but got type: '{type(value)}', value: '{value}'"
        )


class UrlBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> Dict[str, str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            if value:
                return {"text": str(value), "link": str(value)}
            else:
                return None
        raise ValueError(
            f"UrlBitableFieldType escape_out value must be str, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            if "link" in value:
                return value.get("link", None)
            return None
        raise ValueError(
            f"UrlBitableFieldType escape_in value must be str or dict, but got type: '{type(value)}', value: '{value}'"
        )


class UserBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> List[Dict[str, str]] | None:
        if value is None:
            return None
        if isinstance(value, str):
            if value:
                return [{"id": str(value)}]
            else:
                return None
        raise ValueError(
            f"UserBitableFieldType escape_out value must be str, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            if len(value) > 0:
                for item in value:
                    if isinstance(item, dict) and "id" in item:
                        return item.get("id", None)
            return None
        raise ValueError(
            f"UserBitableFieldType escape_in value must be list, but got type: '{type(value)}', value: '{value}'"
        )


class DateTimeBitableFieldType(BaseBitableFieldType):
    _date_formats = [
        "%Y-%m-%d",  # yyyy-MM-dd
        "%Y-%m-%d %H:%M:%S",  # yyyy-MM-dd HH:mm:ss
        "%Y-%m-%dT%H:%M:%S%z",  # ISO format with timezone
    ]

    def escape_out(self, value: datetime | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return int(value.timestamp() * 1000)
        raise ValueError(
            f"DateTimeBitableFieldType escape_out value must be datetime, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, int):
            if value > 0:
                return datetime.fromtimestamp(value / 1000)
            else:
                return None
        raise ValueError(
            f"DateTimeBitableFieldType escape_in value must be int, but got type: '{type(value)}', value: '{value}'"
        )


class SingleSelectBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise ValueError(
            f"SingleSelectBitableFieldType escape_out value must be str, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise ValueError(
            f"SingleSelectBitableFieldType escape_in value must be str, but got type: '{type(value)}', value: '{value}'"
        )


class CheckboxBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: bool | None) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise ValueError(
            f"CheckboxBitableFieldType escape_out value must be bool, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise ValueError(
            f"CheckboxBitableFieldType escape_in value must be bool, but got type: '{type(value)}', value: '{value}'"
        )


class NumberIntBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        raise ValueError(
            f"NumberIntBitableFieldType escape_out value must be int, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        raise ValueError(
            f"NumberIntBitableFieldType escape_in value must be int, but got type: '{type(value)}', value: '{value}'"
        )


class NumberFloatBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: float | None) -> float | None:
        if value is None:
            return None
        if isinstance(value, float):
            return value
        raise ValueError(
            f"NumberFloatBitableFieldType escape_out value must be float, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> float | None:
        if value is None:
            return None
        if isinstance(value, float):
            return value
        raise ValueError(
            f"NumberFloatBitableFieldType escape_in value must be float, but got type: '{type(value)}', value: '{value}'"
        )


class NumberDecimalBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: Decimal | None) -> float | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        raise ValueError(
            f"NumberDecimalBitableFieldType escape_out value must be Decimal, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: float | None) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, (int, float, str)):
            try:
                return Decimal(str(value))
            except:
                raise ValueError(
                    f"NumberDecimalBitableFieldType escape_in value must be valid decimal, but got type: '{type(value)}', value: '{value}'"
                )
        raise ValueError(
            f"NumberDecimalBitableFieldType escape_in value must be number or string, but got type: '{type(value)}', value: '{value}'"
        )


class OneWayAssociationBitableFieldType(BaseBitableFieldType):
    def escape_out(self, value: str | None) -> List[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            return [value]
        raise ValueError(
            f"OneWayAssociationBitableFieldType escape_out value must be str, but got type: '{type(value)}', value: '{value}'"
        )

    def escape_in(self, value: Any | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            if len(value) > 0:
                return value[0]
            return None
        if isinstance(value, dict):
            if "link_record_ids" in value:
                link_record_ids = value.get("link_record_ids", None)
                if isinstance(link_record_ids, list) and len(link_record_ids) > 0:
                    return link_record_ids[0]
            return None
        raise ValueError(
            f"OneWayAssociationBitableFieldType escape_in value must be dict, but got type: '{type(value)}', value: '{value}'"
        )


class BitableFieldType(Enum):
    """多维表格字段类型枚举

    定义了飞书多维表格支持的各种字段类型及其对应的转换器。
    每个枚举值都是一个字段类型转换器实例，负责处理该类型字段的输入输出转换。

    支持的字段类型：
    - TEXT: 文本字段
    - SINGLE_SELECT: 单选字段
    - URL: 链接字段
    - DATE_TIME: 日期时间字段
    - USER: 用户字段
    - CHECKBOX: 复选框字段
    - NUMBER_INT: 整数字段
    - NUMBER_FLOAT: 浮点数字段
    - NUMBER_DECIMAL: 高精度小数字段
    """

    TEXT = TextBitableFieldType()
    URL = UrlBitableFieldType()
    USER = UserBitableFieldType()
    DATE_TIME = DateTimeBitableFieldType()
    SINGLE_SELECT = SingleSelectBitableFieldType()
    CHECKBOX = CheckboxBitableFieldType()

    NUMBER_INT = NumberIntBitableFieldType()
    NUMBER_FLOAT = NumberFloatBitableFieldType()
    NUMBER_DECIMAL = NumberDecimalBitableFieldType()
    ONE_WAY_ASSOCIATION = OneWayAssociationBitableFieldType()
