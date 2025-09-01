import json

from util.json_util import dump_json

from .mock_record import MockRecord, generate_mock_app_table_record
from ..lark_bitable import parse_bitable_record


def main():
    # 模拟从飞书API获取的AppTableRecord数据
    mock_app_table_record = generate_mock_app_table_record()

    # in
    # 使用新的parse_bitable_record函数，直接接受AppTableRecord
    mock_record = parse_bitable_record(MockRecord, mock_app_table_record)
    print("record(mock_record):", dump_json(mock_record))
    print("record_id:", mock_record.record_id)

    # out
    # 使用继承的to_fields方法
    fields = mock_record.to_fields()
    print("fields:", dump_json(fields))


if __name__ == "__main__":
    main()
