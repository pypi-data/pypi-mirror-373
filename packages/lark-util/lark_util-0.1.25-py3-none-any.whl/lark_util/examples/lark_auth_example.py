"""飞书认证示例

展示如何使用lark_auth模块中的认证相关函数：
1. 使用app_id和app_secret获取tenant_access_token
2. 展示token的格式和结构
3. 包含错误处理示例
"""

import logging
import lark_oapi as lark
from ..lark_auth import get_tenant_access_token

# 设置lark-oapi日志级别为INFO
lark.logger.setLevel(logging.INFO)


def main():
    # 示例参数
    app_id = "cli_a4c3f7c9e3f8500d"
    app_secret = "dxLXOj6RLWTWlCvKP8gqZgOZMqOcbWnx"

    try:
        # 示例1: 使用有效的app_id和app_secret获取tenant_access_token
        print("\n示例1: 使用有效的凭证获取tenant_access_token")
        token = get_tenant_access_token(app_id, app_secret)

        # 打印token信息
        print("获取结果:")
        print(f"  Token: {token}")
        print(f"  Token类型: {type(token)}")
        print(f"  Token长度: {len(token)}")

        # 示例2: 使用无效的凭证（展示错误处理）
        print("\n示例2: 使用无效的凭证（错误处理示例）")
        invalid_app_id = "invalid_app_id"
        invalid_app_secret = "invalid_app_secret"

        try:
            invalid_token = get_tenant_access_token(invalid_app_id, invalid_app_secret)
            print("获取结果:")
            print(f"  Token: {invalid_token}")
        except Exception as e:
            print("预期的错误处理:")
            print(f"  错误信息: {e}")

    except Exception as e:
        print(f"\n执行示例时出错: {e}")
        print("请检查app_id和app_secret是否正确配置")


if __name__ == "__main__":
    main()
