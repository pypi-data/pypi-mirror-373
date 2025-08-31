"""飞书多维表格记录处理模块"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import json
from typing import Any, Dict, Type, TypeVar, Tuple
from functools import wraps
from lark_oapi.api.bitable.v1 import AppTableRecord

from .bitable_field_type import BitableFieldType
from . import (
    BITABLE_FIELD_ALIAS,
    BITABLE_FIELD_TYPE,
    IS_BITABLE_PRIMARY_KEY,
    FIELD_RECORD_ID,
    FIELD_LAST_MODIFIED_TIME,
)

T = TypeVar("T", bound="BitableBaseRecord")


@dataclass
class BitableBaseRecord(ABC):
    """飞书多维表格基础记录类"""

    record_id: str | None = field(default=None)
    last_modified_time: datetime | None = field(default=None)

    def to_fields(self, filter_none: bool = True) -> Dict[str, Any]:
        """将对象转换为字典格式
        filter_none: 是否过滤None值, 为True时, 值为None的BitableField字段, 在转化至fields时会被跳过.
        """
        cls = self.__class__
        result = {}
        for field_name, field_obj in cls.__dataclass_fields__.items():
            alias = _get_field_alias(cls, field_name)
            if not alias:
                continue
            # 过滤None值
            value = getattr(self, field_name)
            if filter_none and value is None:
                continue
            result[alias] = _escape_out(cls, field_name, value)
        return result

    @classmethod
    def get_primary_key_alias(cls) -> str:
        """获取主键字段别名

        Returns:
            str: 主键别名

        Raises:
            ValueError: 当找不到主键字段时抛出异常
        """
        for field_name, field_obj in cls.__dataclass_fields__.items():
            if field_obj.metadata.get(IS_BITABLE_PRIMARY_KEY, False):
                primary_key_alias = field_obj.metadata.get(BITABLE_FIELD_ALIAS, "")
                return primary_key_alias
        raise ValueError(f"No primary key field found in {cls.__name__}")

    def get_primary_key_value(self) -> str | int:
        """获取对象的主键值

        Returns:
            str | int: 主键值（非空）

        Raises:
            ValueError: 当找不到主键字段、主键值为空或类型不正确时抛出异常
        """
        cls = self.__class__
        for field_name, field_obj in cls.__dataclass_fields__.items():
            if field_obj.metadata.get(IS_BITABLE_PRIMARY_KEY, False):
                value = getattr(self, field_name)
                if value is None:
                    raise ValueError(f"Primary key value is None in {cls.__name__}")
                if isinstance(value, str):
                    if not value.strip():
                        raise ValueError(
                            f"Primary key value is empty string in {cls.__name__}"
                        )
                    return value
                elif isinstance(value, int):
                    return value
                else:
                    raise ValueError(
                        f"Primary key value must be str or int, got {type(value).__name__} in {cls.__name__}"
                    )
        raise ValueError(f"No primary key field found in {cls.__name__}")


def bitable_field_metadata(
    field_alias: str, field_type: BitableFieldType, is_primary_key: bool = False
) -> Dict[str, Any]:
    """创建多维表格字段元数据"""
    return {
        BITABLE_FIELD_ALIAS: field_alias,
        BITABLE_FIELD_TYPE: field_type,
        IS_BITABLE_PRIMARY_KEY: is_primary_key,
    }


def _escape_out(cls: Any, field_name: str, value: Any) -> Any:
    """字段输出转义"""
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get(BITABLE_FIELD_TYPE)
    if field_type:
        return field_type.value.escape_out(value)
    return value


def _escape_in(cls: Any, field_name: str, value: Any) -> Any:
    """字段输入转义"""
    field_obj = cls.__dataclass_fields__[field_name]
    field_type = field_obj.metadata.get(BITABLE_FIELD_TYPE)
    if field_type:
        return field_type.value.escape_in(value)
    return value


def _get_field_alias(cls: Any, field_name: str) -> str:
    """获取字段别名"""
    field_obj = cls.__dataclass_fields__[field_name]
    return field_obj.metadata.get(BITABLE_FIELD_ALIAS, "")


def parse_bitable_record(cls: Type[T], input: AppTableRecord) -> T:
    """将 AppTableRecord 解析为指定类型的对象"""
    obj = cls()
    # 设置record_id
    if hasattr(input, "record_id") and input.record_id is not None:
        obj.record_id = input.record_id

    # 设置last_modified_time
    if hasattr(input, "last_modified_time") and input.last_modified_time is not None:
        obj.last_modified_time = datetime.fromtimestamp(input.last_modified_time / 1000)

    # 处理fields字段
    fields = input.fields if hasattr(input, "fields") and input.fields else {}
    for field_name, field_obj in cls.__dataclass_fields__.items():
        if field_name in [
            FIELD_RECORD_ID,
            FIELD_LAST_MODIFIED_TIME,
        ]:  # BitableBaseRecord
            continue
        alias = _get_field_alias(cls, field_name)
        if alias in fields:
            setattr(obj, field_name, _escape_in(cls, field_name, fields[alias]))
    return obj


def bitable_record(table_id: str, view_id: str):
    """飞书多维表格记录装饰器

    用于标注实体类的 table_id 和 view_id

    Args:
        table_id: 多维表格的表格ID
        view_id: 多维表格的视图ID

    Returns:
        装饰后的类，添加了 _table_id 和 _view_id 属性

    Example:
        @bitable_record(table_id="tblXXX", view_id="vewYYY")
        class Product(BitableBaseRecord):
            pass
    """

    def decorator(cls: Type[T]) -> Type[T]:
        # 为类添加表格和视图ID属性
        cls._table_id = table_id
        cls._view_id = view_id

        # 添加获取表格ID的类方法
        @classmethod
        def get_table_id(cls) -> str:
            """获取表格ID"""
            return cls._table_id

        # 添加获取视图ID的类方法
        @classmethod
        def get_view_id(cls) -> str:
            """获取视图ID"""
            return cls._view_id

        # 将方法绑定到类上
        cls.get_table_id = get_table_id
        cls.get_view_id = get_view_id

        return cls

    return decorator
