# 字符串常量定义

# 字段名常量
FIELD_RECORD_ID = "record_id"
FIELD_LAST_MODIFIED_TIME = "last_modified_time"

# 用户ID类型常量
USER_ID_TYPE = "user_id"

# 字段键名常量
BITABLE_FIELD_ALIAS = "bitable_field_alias"
BITABLE_FIELD_TYPE = "bitable_field_type"
IS_BITABLE_PRIMARY_KEY = "is_bitable_primary_key"


# 条件连接符常量
CONJUNCTION_AND = "and"
CONJUNCTION_OR = "or"

# 搜索操作符常量
OPERATOR_IS = "is"
OPERATOR_IS_NOT = "isNot"
OPERATOR_CONTAINS = "contains"
OPERATOR_DOES_NOT_CONTAIN = "doesNotContain"
OPERATOR_IS_EMPTY = "isEmpty"
OPERATOR_IS_NOT_EMPTY = "isNotEmpty"
OPERATOR_IS_GREATER = "isGreater"
OPERATOR_IS_GREATER_EQUAL = "isGreaterEqual"
OPERATOR_IS_LESS = "isLess"
OPERATOR_IS_LESS_EQUAL = "isLessEqual"
OPERATOR_LIKE = "like"  # LIKE 运算符。暂未支持
OPERATOR_IN = "in"  # IN 运算符。暂未支持

# 错误消息常量
ERROR_RECORD_ID_MUST_BE_EMPTY = "创建记录时record_id必须为空"
ERROR_RECORD_ID_CANNOT_BE_EMPTY = "更新记录时record_id不能为空"
ERROR_PRIMARY_KEY_MUST_BE_PROVIDED = "Primary key field must be provided"
ERROR_PRIMARY_KEY_MUST_BE_UNIQUE = "Primary key must be unique"

from .bitable_field_type import BitableFieldType
from .create_bitable_record import create_bitable_record
from .delete_bitable_record import delete_bitable_record
from .bitable_record import (
    BitableBaseRecord,
    parse_bitable_record,
    bitable_field_metadata,
    bitable_record,
)
from .search_bitable_records import search_bitable_records
from .update_bitable_record import update_bitable_record
from .bitable_record_service import BitableRecordService

__all__ = [
    # 常量
    "USER_ID_TYPE",
    "BITABLE_FIELD_ALIAS",
    "BITABLE_FIELD_TYPE",
    "IS_BITABLE_PRIMARY_KEY",
    "OPERATOR_IS",
    "OPERATOR_IS_NOT",
    "OPERATOR_CONTAINS",
    "OPERATOR_DOES_NOT_CONTAIN",
    "OPERATOR_IS_EMPTY",
    "OPERATOR_IS_NOT_EMPTY",
    "OPERATOR_IS_GREATER",
    "OPERATOR_IS_GREATER_EQUAL",
    "OPERATOR_IS_LESS",
    "OPERATOR_IS_LESS_EQUAL",
    "OPERATOR_LIKE",
    "OPERATOR_IN",
    "CONJUNCTION_AND",
    "CONJUNCTION_OR",
    "FIELD_RECORD_ID",
    "FIELD_LAST_MODIFIED_TIME",
    "ERROR_RECORD_ID_MUST_BE_EMPTY",
    "ERROR_RECORD_ID_CANNOT_BE_EMPTY",
    "ERROR_PRIMARY_KEY_MUST_BE_PROVIDED",
    "ERROR_PRIMARY_KEY_MUST_BE_UNIQUE",
    # 函数和类
    "create_bitable_record",
    "delete_bitable_record",
    "search_bitable_records",
    "update_bitable_record",
    "BitableFieldType",
    "BitableBaseRecord",
    "bitable_field_metadata",
    "parse_bitable_record",
    "bitable_record",
    "BitableRecordService",
]
