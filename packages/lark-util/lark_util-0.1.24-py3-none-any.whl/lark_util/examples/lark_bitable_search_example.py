"""飞书多维表格搜索记录示例"""

import os
import lark_oapi as lark

from lark_util.examples.mock_record import APP_TOKEN, TABLE_ID, VIEW_ID
from util.json_util import dump_json
from ..lark_bitable import search_bitable_records


def main():

    try:
        result = search_bitable_records(
            APP_TOKEN,
            TABLE_ID,
            VIEW_ID,
        )
        print(f"搜索记录成功: {dump_json(result)}")
    except Exception as e:
        print(f"搜索记录失败: {e}")


if __name__ == "__main__":
    main()
