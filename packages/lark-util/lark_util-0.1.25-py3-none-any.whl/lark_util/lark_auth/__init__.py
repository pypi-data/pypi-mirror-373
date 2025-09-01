"""
飞书认证模块

基于官方lark-oapi SDK的认证功能
"""

from .get_tenant_access_token import get_tenant_access_token

__all__ = ["get_tenant_access_token"]
