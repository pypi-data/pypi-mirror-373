"""
飞书客户端模块

基于官方lark-oapi SDK的客户端初始化工具
"""

import os
import lark_oapi as lark
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取配置并存储为常量
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")

# 验证必要配置
if not APP_ID or not APP_SECRET:
    raise ValueError("请设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")

# 初始化客户端
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()

__all__ = ["client", "APP_ID", "APP_SECRET"]
