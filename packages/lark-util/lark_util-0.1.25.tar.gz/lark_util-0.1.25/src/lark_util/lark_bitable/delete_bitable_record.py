"""飞书多维表格删除记录模块

基于官方lark-oapi SDK的多维表格删除功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    DeleteAppTableRecordRequest,
    DeleteAppTableRecordResponse,
)
from typing import Optional

from ..lark_client import client


def delete_bitable_record(
    app_token: str,
    table_id: str,
    record_id: str,
) -> bool:
    """
    删除多维表格记录

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        record_id: 记录ID

    Returns:
        bool: 删除成功返回True

    Raises:
        Exception: 删除记录失败时抛出异常
    """
    # 构造请求对象
    request = (
        DeleteAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .build()
    )

    # 发起请求
    response: DeleteAppTableRecordResponse = client.bitable.v1.app_table_record.delete(
        request
    )

    # 处理失败返回
    if not response.success():
        error_msg = f"删除多维表格记录失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, 入参: app_token={app_token}, table_id={table_id}, record_id={record_id}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    # 删除成功
    return True
