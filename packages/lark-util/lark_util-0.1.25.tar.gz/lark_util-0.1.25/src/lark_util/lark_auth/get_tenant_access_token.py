"""飞书认证工具

基于官方lark-oapi SDK的认证功能
"""

import json
import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_tenant_access_token() -> str:
    """
    获取tenant_access_token

    Returns:
        tenant_access_token字符串

    Raises:
        Exception: 获取token失败时抛出异常
    """
    import lark_oapi as lark
    from lark_oapi.api.auth.v3 import (
        InternalTenantAccessTokenRequest,
        InternalTenantAccessTokenRequestBody,
    )

    # 从lark_client获取配置常量
    from ..lark_client import APP_ID, APP_SECRET

    # 从lark_client获取client
    from ..lark_client import client

    # 构造请求对象
    request = (
        InternalTenantAccessTokenRequest.builder()
        .request_body(
            InternalTenantAccessTokenRequestBody.builder()
            .app_id(APP_ID)
            .app_secret(APP_SECRET)
            .build()
        )
        .build()
    )

    # 发起请求
    response = client.auth.v3.tenant_access_token.internal(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"获取tenant_access_token失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise Exception(error_msg)

    # 从raw.content中解析token
    if response.raw and response.raw.content:
        try:
            response_data = json.loads(response.raw.content.decode("utf-8"))
            return response_data.get("tenant_access_token")
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"解析响应数据失败: {e}"
            lark.logger.error(error_msg)
            raise Exception(error_msg)
    else:
        raise Exception("响应数据为空")
