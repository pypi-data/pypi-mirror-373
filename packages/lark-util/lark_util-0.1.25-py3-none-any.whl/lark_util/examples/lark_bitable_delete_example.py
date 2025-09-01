"""飞书多维表格删除记录示例"""

import os
import lark_oapi as lark

from lark_util.examples.mock_record import (
    APP_TOKEN,
    TABLE_ID,
    generate_empty_mock_record,
)
from util.json_util import dump_json
from ..lark_bitable import create_bitable_record, delete_bitable_record


def main():
    # 字段值
    mock_fields = generate_empty_mock_record().to_fields()

    try:
        # 先创建一条记录
        create_result = create_bitable_record(APP_TOKEN, TABLE_ID, mock_fields)
        record_id = create_result.record_id
        print(f"创建记录成功: created_result={dump_json(create_result)}")

        # 使用创建的record_id进行删除
        delete_result = delete_bitable_record(APP_TOKEN, TABLE_ID, record_id)
        print(f"删除记录成功: deleted_result={dump_json(delete_result)}")

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    main()
