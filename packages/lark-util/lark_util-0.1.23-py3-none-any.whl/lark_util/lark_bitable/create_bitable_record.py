"""飞书多维表格创建记录模块

基于官方lark-oapi SDK的多维表格创建功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    CreateAppTableRecordRequest,
    AppTableRecord,
    CreateAppTableRecordResponse,
    CreateAppTableRecordResponseBody,
)
from typing import Dict, Any, Optional

from ..lark_client import client
from . import USER_ID_TYPE


def create_bitable_record(
    app_token: str,
    table_id: str,
    fields: Dict[str, Any],
) -> AppTableRecord:
    """
    新增多维表格记录

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        fields: 字段值字典，key为字段名，value为字段值

    Returns:
        AppTableRecord: 新增的记录数据

    Raises:
        Exception: 新增记录失败时抛出异常
    """
    # 构造请求对象
    request = (
        CreateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .user_id_type(USER_ID_TYPE)
        .request_body(AppTableRecord.builder().fields(fields).build())
        .build()
    )

    # 发起请求
    response: CreateAppTableRecordResponse = client.bitable.v1.app_table_record.create(
        request
    )

    # 处理失败返回
    if not response.success():
        error_msg = f"新增多维表格记录失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, 入参: app_token={app_token}, table_id={table_id}, fields={json.dumps(fields, ensure_ascii=False)}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    # 返回新增的记录数据
    return response.data.record
