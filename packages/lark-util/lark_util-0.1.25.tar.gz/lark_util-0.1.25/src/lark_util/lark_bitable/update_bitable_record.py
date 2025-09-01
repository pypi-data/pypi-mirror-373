"""飞书多维表格更新记录模块

基于官方lark-oapi SDK的多维表格更新功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    UpdateAppTableRecordRequest,
    AppTableRecord,
    UpdateAppTableRecordResponse,
    UpdateAppTableRecordResponseBody,
)
from typing import Dict, Any, Optional
from ..lark_client import client
from . import USER_ID_TYPE


def update_bitable_record(
    app_token: str,
    table_id: str,
    record_id: str,
    fields: Dict[str, Any],
) -> AppTableRecord:
    """
    更新多维表格记录

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        record_id: 记录ID
        fields: 字段值字典，key为字段名，value为字段值

    Returns:
        AppTableRecord: 更新后的记录数据

    Raises:
        Exception: 更新记录失败时抛出异常
    """
    # 构造请求对象
    request = (
        UpdateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .user_id_type(USER_ID_TYPE)
        .request_body(AppTableRecord.builder().fields(fields).build())
        .build()
    )

    # 发起请求
    response: UpdateAppTableRecordResponse = client.bitable.v1.app_table_record.update(
        request
    )

    # 处理失败返回
    if not response.success():
        error_msg = f"更新多维表格记录失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, 入参: app_token={app_token}, table_id={table_id}, record_id={record_id}, fields={json.dumps(fields, ensure_ascii=False)}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    return response.data.record
