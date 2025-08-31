"""飞书多维表格记录服务示例"""

from datetime import datetime
from lark_util.examples.mock_record import APP_TOKEN, MockRecord, generate_empty_mock_record
from util.json_util import dump_json
from ..lark_bitable import (
    BitableRecordService,
)


def main():

    # 创建服务实例
    service = BitableRecordService(APP_TOKEN, MockRecord)

    mock_record = generate_empty_mock_record()

    try:
        record = service.create(mock_record)
        print(f"创建记录成功: {dump_json(record)}")

        try:
            record = service.create(mock_record)
            print(f"重复pk创建记录成功: {dump_json(record)}")  # pk
        except Exception as e:
            print(f"重复pk创建记录失败: {e}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"搜索记录成功，记录ID: {dump_json(record)}")
        record.text = "2234"
        record = service.update(record)
        print(f"更新记录成功: {dump_json(record)}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"乐观锁冲突, 搜索记录成功，记录ID: {dump_json(record)}")
        record.last_modified_time = datetime.fromtimestamp(0)
        print(f"乐观锁冲突, 手动更改last_modified_time为0")
        record.text = "3345"
        try:
            record = service.update(record)  # 乐观锁
            print(f"乐观锁冲突, 更新记录成功: {dump_json(record)}")
        except Exception as e:
            print(f"乐观锁冲突, 更新记录失败: {e}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"强制更新, 搜索记录成功，记录ID: {dump_json(record)}")
        record.last_modified_time = datetime.fromtimestamp(0)
        print(f"强制更新, 手动更改last_modified_time为0")
        record.text = "4456"
        record = service.update(record, force_update=True)  # force update
        print(f"强制更新, 更新记录成功: {dump_json(record)}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"save, 搜索记录成功，记录ID: {dump_json(record)}")
        record.record_id = None
        try:
            service.save(record)
            print(f"save, 重复pk, 保存记录成功: {dump_json(record)}")
        except Exception as e:
            print(f"save, 重复pk, 保存记录失败: {e}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"save, 搜索记录成功，记录ID: {dump_json(record)}")
        record.record_id = None
        try:
            service.save(record, force_update=True)
            print(f"save, 重复pk创建, 强制更新, 保存记录成功: {dump_json(record)}")
        except Exception as e:
            print(f"save, 重复pk创建, 强制更新, 保存记录失败: {e}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"save, 搜索记录成功，记录ID: {dump_json(record)}")
        record.last_modified_time = datetime.fromtimestamp(0)
        print(f"save, 手动更改last_modified_time为0")
        record.text = "5567"
        try:
            service.save(record)
            print(f"save, 乐观锁冲突 保存记录成功: {dump_json(record)}")
        except Exception as e:
            print(f"save, 乐观锁冲突, 保存记录失败: {e}")

        pk = mock_record.get_primary_key_value()
        record = service.search_by_primary_key(pk)
        print(f"save, 搜索记录成功，记录ID: {dump_json(record)}")
        record.last_modified_time = datetime.fromtimestamp(0)
        print(f"save, 手动更改last_modified_time为0")
        record.text = "5567"
        service.save(record, force_update=True)
        print(f"save, 乐观锁冲突 保存记录成功: {dump_json(record)}")

        # mock_record.number_int = 999
        # updated_record = service.save(mock_record)

        # # 搜索记录
        # print("\n=== 搜索记录 ===")
        # records, total = service.search_all(limit=5)
        # print(f"搜索到 {len(records)} 条记录，总计 {total} 条")
        # for record in records:
        #     print(
        #         f"  - record_id: {record.record_id}, product_name: {record.product_name}"
        #     )

    except Exception as e:
        print(f"操作失败: {e}")


if __name__ == "__main__":
    main()
