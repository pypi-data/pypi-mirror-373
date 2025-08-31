"""飞书知识空间示例

展示如何使用lark_space模块中的函数：
1. 获取不同类型的知识空间节点信息
2. 展示节点的完整结构
3. 包含错误处理示例
"""

import logging
import lark_oapi as lark
from ..lark_space import get_space_node

# 设置lark-oapi日志级别为INFO
lark.logger.setLevel(logging.INFO)


def main():
    # 示例参数
    # wiki_token = "wikcnMhxxx1GWUkQWvhqNXtLvqg"
    wiki_token = "wikcnMhxxx1GWUkQWvhqNXtLvqh"

    try:
        # 示例: 获取Wiki类型的节点
        print("\n示例1: 获取Wiki类型的节点信息")
        wiki_node = get_space_node(token=wiki_token, obj_type="wiki")

        # 打印节点信息
        print("节点信息:")
        print("完整的节点结构:")
        print(lark.JSON.marshal(wiki_node, indent=2))

    except Exception as e:
        print(f"\n执行示例时出错: {e}")
        print("请检查token是否正确配置，以及是否具有相应的访问权限")


if __name__ == "__main__":
    main()
