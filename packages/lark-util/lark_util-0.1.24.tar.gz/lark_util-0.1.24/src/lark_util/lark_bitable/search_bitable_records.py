"""飞书多维表格搜索记录模块

基于官方lark-oapi SDK的多维表格搜索功能
"""

import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import (
    SearchAppTableRecordRequest,
    SearchAppTableRecordRequestBody,
    SearchAppTableRecordResponse,
    SearchAppTableRecordResponseBody,
    FilterInfo,
    Condition,
    Sort,
)
from typing import Dict, Any, List, Tuple
from ..lark_client import client
from . import USER_ID_TYPE


def search_bitable_records(
    app_token: str,
    table_id: str,
    view_id: str,
    field_names: List[str] | None = None,
    conjunction: str | None = None,
    conditions: List[Tuple[str, str, List[str]]] | None = None,
    sorts: List[Tuple[str, bool]] | None = None,
    page_token: str | None = None,
    page_size: int = 20,
) -> SearchAppTableRecordResponseBody:
    """
    搜索多维表格记录

    Args:
        app_token: 多维表格应用token
        table_id: 表格ID
        view_id: 视图ID
        field_names: 要返回的字段名列表，默认为None（返回所有字段）
        conjunction: 条件连接符，可选值为"and"或"or"，默认为None
        conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
            支持的操作符：
            - is：等于
            - isNot：不等于（不支持日期字段，了解如何查询日期字段，参考日期字段填写说明）
            - contains：包含（不支持日期字段）
            - doesNotContain：不包含（不支持日期字段）
            - isEmpty：为空
            - isNotEmpty：不为空
            - isGreater：大于
            - isGreaterEqual：大于等于（不支持日期字段）
            - isLess：小于
            - isLessEqual：小于等于（不支持日期字段）
            - like：LIKE 运算符。暂未支持
            - in：IN 运算符。暂未支持
        sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
        page_token: 分页标记，默认为None
        page_size: 每页记录数，默认为20

    Returns:
        SearchAppTableRecordResponseBody: 多维表格记录响应对象，包含items、has_more、page_token和total等信息

    Raises:
        Exception: 搜索记录失败时抛出异常
    """
    # 构造请求对象
    request_builder = (
        SearchAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .user_id_type(USER_ID_TYPE)
        .page_size(page_size)
    )

    # 如果提供了page_token，添加到请求中
    if page_token:
        request_builder.page_token(page_token)

    # 构造请求体
    request_body_builder = SearchAppTableRecordRequestBody.builder()

    # 添加视图ID到请求体中
    request_body_builder.view_id(view_id)

    # 添加字段名列表（如果提供）
    if field_names:
        request_body_builder.field_names(field_names)

    # 添加排序条件（如果提供）
    if sorts:
        sort_list = []
        for field_name, desc in sorts:
            sort_list.append(Sort.builder().field_name(field_name).desc(desc).build())
        request_body_builder.sort(sort_list)

    # 添加筛选条件（如果提供）
    if conjunction and conditions:
        condition_list = []
        for field_name, operator, values in conditions:
            condition_list.append(
                Condition.builder()
                .field_name(field_name)
                .operator(operator)
                .value(values)
                .build()
            )

        filter_info = (
            FilterInfo.builder()
            .conjunction(conjunction)
            .conditions(condition_list)
            .build()
        )

        request_body_builder.filter(filter_info)

        request_body_builder.automatic_fields(True)

    # 完成请求构建
    request = request_builder.request_body(request_body_builder.build()).build()

    # 发起请求
    response = client.bitable.v1.app_table_record.search(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"搜索多维表格记录失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, 入参: app_token={app_token}, table_id={table_id}, view_id={view_id}, field_names={field_names}, conjunction={conjunction}, conditions={conditions}, sorts={sorts}, page_token={page_token}, page_size={page_size}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    # 返回response.data对象
    return response.data
