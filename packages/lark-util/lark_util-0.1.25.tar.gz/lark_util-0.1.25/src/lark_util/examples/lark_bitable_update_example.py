"""飞书多维表格更新记录示例"""

import os
import lark_oapi as lark

from lark_util.examples.mock_record import generate_empty_mock_record
from lark_util.examples.mock_record import APP_TOKEN, TABLE_ID
from lark_util.lark_bitable import create_bitable_record
from util.json_util import dump_json
from ..lark_bitable import update_bitable_record


def main():

    # 字段值
    mock_fields = generate_empty_mock_record().to_fields()

    # 新增记录
    try:
        result = create_bitable_record(APP_TOKEN, TABLE_ID, mock_fields)
        print(f"新增记录成功: {dump_json(result)}")
    except Exception as e:
        print(f"新增记录失败: {e}")

    # 更新记录
    mock_fields["number_int"] = 12345
    try:
        result = update_bitable_record(
            APP_TOKEN, TABLE_ID, result.record_id, mock_fields
        )
        print(f"更新记录成功: {dump_json(result)}")
    except Exception as e:
        print(f"更新记录失败: {e}")


if __name__ == "__main__":
    main()
