"""飞书多维表格产品数据模型"""

from dataclasses import dataclass, field
import datetime
from decimal import Decimal
from re import S
from typing import Any, Dict


from ..lark_bitable import BitableFieldType, bitable_field_metadata, bitable_record
from ..lark_bitable.bitable_record import BitableBaseRecord, parse_bitable_record

APP_TOKEN = "AXYab8AxaaMHWSsr8qmczS3hnWA"
TABLE_ID = "tblJwbXfXRGVjQYZ"
VIEW_ID = "vewVRZLhiK"


@bitable_record(table_id=TABLE_ID, view_id=VIEW_ID)
@dataclass
class MockRecord(BitableBaseRecord):

    fake_record_id: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="record_id", field_type=BitableFieldType.TEXT
        ),
    )
    # TEXT 字段类型
    text: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="text", field_type=BitableFieldType.TEXT
        ),
    )
    # URL 字段类型
    url: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="url", field_type=BitableFieldType.URL
        ),
    )
    # USER 字段类型
    user: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="user", field_type=BitableFieldType.USER
        ),
    )
    # DATE_TIME 字段类型
    date_time: datetime.datetime | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="date_time", field_type=BitableFieldType.DATE_TIME
        ),
    )
    # SINGLE_SELECT 字段类型
    single_select: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="single_select", field_type=BitableFieldType.SINGLE_SELECT
        ),
    )
    # CHECKBOX 字段类型
    checkbox: bool | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="checkbox", field_type=BitableFieldType.CHECKBOX
        ),
    )
    # NUMBER_INT 字段类型
    number_int: int | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="number_int",
            field_type=BitableFieldType.NUMBER_INT,
            is_primary_key=True,
        ),
    )
    # NUMBER_FLOAT 字段类型
    number_float: float | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="number_float", field_type=BitableFieldType.NUMBER_FLOAT
        ),
    )
    # NUMBER_DECIMAL 字段类型
    number_decimal: Decimal | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="number_decimal", field_type=BitableFieldType.NUMBER_DECIMAL
        ),
    )
    # ONE_WAY_ASSOCIATION 字段类型
    one_way_association: str | None = field(
        default=None,
        metadata=bitable_field_metadata(
            field_alias="one_way_association",
            field_type=BitableFieldType.ONE_WAY_ASSOCIATION,
        ),
    )


def generate_empty_mock_record() -> MockRecord:
    record = generate_mock_app_table_record()
    record.record_id = None
    record.fields.pop("record_id", None)
    return parse_bitable_record(MockRecord, record)


def generate_mock_app_table_record():
    """创建测试用的AppTableRecord对象"""
    from lark_oapi.api.bitable.v1 import AppTableRecord
    from datetime import datetime

    mock_fields = generate_escape_in_mock_fields()
    mock_fields["record_id"] = "fake_record_id_1"

    return (
        AppTableRecord.builder()
        .record_id("rec123456")
        .last_modified_time(int(datetime.now().timestamp() * 1000))
        .fields(mock_fields)
        .build()
    )


def generate_escape_in_mock_fields() -> Dict[str, Any]:
    return {
        "text": "abcd4",
        "url": {"type": "text", "link": "https://www.google.com/4"},
        "user": [{"id": "2ge1ge5d"}],
        "date_time": 1754755200000,
        "single_select": "opt1",
        "checkbox": True,
        "number_int": 432,
        "number_float": 4.32,
        "number_decimal": 4.987654321,
        "one_way_association": {"link_record_ids": ["recuTRupVOncnk"]},
    }
