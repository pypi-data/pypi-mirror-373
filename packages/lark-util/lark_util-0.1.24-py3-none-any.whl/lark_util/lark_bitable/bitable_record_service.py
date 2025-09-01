"""飞书多维表格记录服务类

基于官方lark-oapi SDK的多维表格操作功能，提供统一的服务接口
"""

import json
import re
from typing import Dict, Any, List, Tuple, TypeVar, Type, Generic, Callable
import lark_oapi as lark

from .create_bitable_record import create_bitable_record
from .search_bitable_records import search_bitable_records
from .update_bitable_record import update_bitable_record
from .bitable_record import BitableBaseRecord, parse_bitable_record
from . import (
    ERROR_RECORD_ID_MUST_BE_EMPTY,
    ERROR_RECORD_ID_CANNOT_BE_EMPTY,
    ERROR_PRIMARY_KEY_MUST_BE_PROVIDED,
    ERROR_PRIMARY_KEY_MUST_BE_UNIQUE,
    OPERATOR_IS,
    CONJUNCTION_AND,
    FIELD_LAST_MODIFIED_TIME,
    OPERATOR_IS_EMPTY,
    OPERATOR_IS_NOT_EMPTY,
)

T = TypeVar("T", bound=BitableBaseRecord)


class BitableRecordService(Generic[T]):
    """飞书多维表格记录服务类

    支持泛型操作，提供创建、更新、查询功能
    """

    def __init__(self, app_token: str, model_cls: Type[T], default_batch: int = 100):
        """初始化服务

        Args:
            app_token: 多维表格应用token
            model_cls: 业务对象类型，必须是BitableBaseRecord的子类
            default_batch: 默认批次大小，默认100
        """
        self.app_token = app_token
        self.model_cls = model_cls
        self.default_batch = default_batch

        # 获取primary_key字段别名
        self.primary_key_alias = model_cls.get_primary_key_alias()

    def create(self, model: T) -> T:
        """创建多维表格记录

        Args:
            model: 业务对象，record_id必须为空

        Returns:
            T: 创建后的业务对象，包含record_id

        Raises:
            ValueError: 当record_id不为空时抛出异常
        """
        if model.record_id is not None and model.record_id != "":
            raise ValueError(ERROR_RECORD_ID_MUST_BE_EMPTY)

        # 校验主键对应的记录必须不存在
        primary_key = self._validate_primary_key(model)
        existing_record = self._search_by_primary_key_with_retry(primary_key)
        if existing_record:
            raise ValueError(f"主键{primary_key}对应的记录已存在，无法创建重复记录")

        # 从装饰器获取table_id
        table_id = self.model_cls.get_table_id()

        # 将业务对象转换为字段值字典
        fields = model.to_fields()

        # 创建记录
        record = create_bitable_record(self.app_token, table_id, fields)

        # 从返回的记录解析为业务对象
        return parse_bitable_record(self.model_cls, record)

    def update(
        self,
        current_model: T,
        force_update: bool = False,
        filter_none: bool = True,
        retry_count: int = 3,
    ) -> T:
        """更新多维表格记录

        Args:
            model: 业务对象，必须包含record_id
            force_update: 是否强制更新，跳过乐观锁校验
            filter_none: 是否过滤None值
            retry_count: 查询记录的重试次数，默认3次

        Returns:
            T: 更新后的业务对象

        Raises:
            ValueError: 当record_id为空时抛出异常
            ValueError: 当乐观锁校验失败时抛出异常
        """
        if current_model.record_id is None or current_model.record_id == "":
            raise ValueError(ERROR_RECORD_ID_CANNOT_BE_EMPTY)

        # 乐观锁校验
        if not force_update:

            # 根据主键查询当前记录，支持重试
            primary_key = self._validate_primary_key(current_model)
            current_record = self._search_by_primary_key_with_retry(
                primary_key, retry_count
            )
            if not current_record:
                raise ValueError(
                    f"根据主键{primary_key}未找到对应记录，已重试{retry_count}次"
                )

            current_model_last_modified_time = current_model.last_modified_time
            current_record_last_modified_time = current_record.last_modified_time
            if current_model_last_modified_time != current_record_last_modified_time:
                raise ValueError(
                    f"记录已被其他用户修改，请重新获取最新数据后再更新。"
                    f"当前记录最后修改时间: {current_record_last_modified_time}, "
                    f"待更新记录最后修改时间: {current_model_last_modified_time}"
                )

        # 从装饰器获取table_id
        table_id = self.model_cls.get_table_id()

        # 将业务对象转换为字段值字典
        fields = current_model.to_fields(filter_none=filter_none)

        result = update_bitable_record(
            self.app_token, table_id, current_model.record_id, fields
        )

        # 从返回的记录解析为业务对象
        return parse_bitable_record(self.model_cls, result)

    def save(
        self,
        model: T,
        force_update: bool = False,
        filter_none: bool = True,
        retry_count: int = 3,
    ) -> T:
        """保存记录

        如果记录有record_id则更新，否则创建新记录

        Args:
            model: 业务对象
            force: 是否强制更新，跳过乐观锁校验
            filter_none: 是否过滤None值
            retry_count: 查询记录的重试次数，默认3次

        Returns:
            T: 保存后的业务对象
        """
        if model.record_id is not None and model.record_id != "":
            return self.update(
                model,
                force_update=force_update,
                filter_none=filter_none,
                retry_count=retry_count,
            )
        else:
            return self.create(model)

    def search(
        self,
        field_names: List[str] | None = None,
        conjunction: str | None = None,
        conditions: List[Tuple[str, str, List[str]]] | None = None,
        sorts: List[Tuple[str, bool]] | None = None,
        limit: int | None = None,
        batch: int | None = None,
    ) -> Tuple[List[T], int]:
        """搜索多维表格记录，支持分页

        Args:
            field_names: 要返回的字段名列表，默认为None（返回所有字段）
            conjunction: 条件连接符，可选值为"and"或"or"，默认为None
            conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
            sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
            limit: 限制返回的记录数量，如果不提供则返回所有记录
            batch: 批次大小，如果不提供则使用default_batch

        Returns:
            Tuple[List[T], int]: 业务对象列表，以及总记录数
        """
        # 从装饰器获取table_id和view_id
        table_id = self.model_cls.get_table_id()
        view_id = self.model_cls.get_view_id()

        all_records = []
        page_token = None
        total = 0
        collected_count = 0

        # 确定使用的批次大小
        current_batch = batch if batch is not None else self.default_batch

        while True:
            # 如果设置了limit，计算本次请求的batch_size
            current_batch_size = current_batch
            if limit is not None:
                remaining = limit - collected_count
                if remaining <= 0:
                    break
                current_batch_size = min(current_batch, remaining)

            result = search_bitable_records(
                self.app_token,
                table_id,
                view_id,
                field_names,
                conjunction,
                conditions,
                sorts,
                page_token,
                current_batch_size,
            )

            # 更新分页状态
            page_token = result.page_token
            total = result.total

            # 解析记录为业务对象
            for item in result.items:
                business_obj = parse_bitable_record(self.model_cls, item)
                all_records.append(business_obj)
                collected_count += 1

                # 如果达到limit，停止收集
                if limit is not None and collected_count >= limit:
                    break

            # 如果没有更多记录或已达到limit，退出循环
            if not result.has_more or (limit is not None and collected_count >= limit):
                break

        return all_records, total

    def search_and_process_batch(
        self,
        process_func: Callable[[List[T]], None],
        field_names: List[str] | None = None,
        conjunction: str | None = None,
        conditions: List[Tuple[str, str, List[str]]] | None = None,
        sorts: List[Tuple[str, bool]] | None = None,
        limit: int | None = None,
        batch: int | None = None,
    ) -> None:
        """搜索记录并批量处理

        Args:
            process_func: 处理函数，接收List[T]，无返回值
            field_names: 要返回的字段名列表，默认为None（返回所有字段）
            conjunction: 条件连接符，可选值为"and"或"or"，默认为None
            conditions: 筛选条件列表，每个条件为(字段名, 操作符, 值列表)的三元组，默认为None
            sorts: 排序条件列表，每个条件为(字段名, 是否降序)的二元组，默认为None
            limit: 限制返回的记录数量，如果不提供则返回所有记录
            batch: 批次大小，如果不提供则使用default_batch
        """
        # 从装饰器获取table_id和view_id
        table_id = self.model_cls.get_table_id()
        view_id = self.model_cls.get_view_id()

        page_token = None
        collected_count = 0

        # 确定使用的批次大小
        current_batch = batch if batch is not None else self.default_batch

        while True:
            # 如果设置了limit，计算本次请求的batch_size
            current_batch_size = current_batch
            if limit is not None:
                remaining = limit - collected_count
                if remaining <= 0:
                    break
                current_batch_size = min(current_batch, remaining)

            result = search_bitable_records(
                self.app_token,
                table_id,
                view_id,
                field_names,
                conjunction,
                conditions,
                sorts,
                page_token,
                current_batch_size,
            )

            # 解析记录为业务对象
            batch_records = []
            for item in result.items:
                business_obj = parse_bitable_record(self.model_cls, item)
                batch_records.append(business_obj)
                collected_count += 1

                # 如果达到limit，停止收集
                if limit is not None and collected_count >= limit:
                    break

            # 处理当前批次的记录
            if batch_records:
                process_func(batch_records)

            # 如果没有更多记录或已达到limit，退出循环
            if not result.has_more or (limit is not None and collected_count >= limit):
                break

            page_token = result.page_token

    def search_primary_key_not_empty(self) -> Tuple[List[T], int]:
        if not self.primary_key_alias:
            raise ValueError(ERROR_PRIMARY_KEY_MUST_BE_PROVIDED)

        return self.search(
            conjunction=CONJUNCTION_AND,
            conditions=[(self.primary_key_alias, OPERATOR_IS_NOT_EMPTY, [])],
        )

    def search_primary_key_empty(self) -> Tuple[List[T], int]:
        if not self.primary_key_alias:
            raise ValueError(ERROR_PRIMARY_KEY_MUST_BE_PROVIDED)

        return self.search(
            conjunction=CONJUNCTION_AND,
            conditions=[(self.primary_key_alias, OPERATOR_IS_EMPTY, [])],
        )

    def search_by_primary_key(self, primary_key: Any) -> T | None:
        """根据主键搜索记录

        Args:
            primary_key: 主键值

        Returns:
            T | None: 找到的记录对象，如果未找到则返回None

        Raises:
            ValueError: 当主键字段未定义或主键值为空时抛出异常
        """
        if primary_key is None or not self.primary_key_alias:
            raise ValueError(ERROR_PRIMARY_KEY_MUST_BE_PROVIDED)

        records, total = self.search(
            conjunction=CONJUNCTION_AND,
            conditions=[(self.primary_key_alias, OPERATOR_IS, [primary_key])],
        )
        if total == 0:
            return None
        if len(records) > 1:
            raise ValueError(ERROR_PRIMARY_KEY_MUST_BE_UNIQUE)
        if len(records) > 0:
            return records[0]
        return None

    def _validate_primary_key(self, model: T) -> str | int:
        """校验主键值的有效性

        Args:
            model: 业务对象

        Returns:
            str | int: 有效的主键值

        Raises:
            ValueError: 当主键值无效时抛出异常
        """
        primary_key = model.get_primary_key_value()

        # 校验主键类型和非空
        if primary_key is None:
            raise ValueError("主键值不能为空")
        if not isinstance(primary_key, (str, int)):
            raise ValueError(
                f"主键值必须是字符串或整数类型，当前类型: {type(primary_key).__name__}"
            )
        if isinstance(primary_key, str) and not primary_key.strip():
            raise ValueError("主键值不能为空字符串")

        return primary_key

    def _search_by_primary_key_with_retry(
        self, primary_key: str | int, retry_count: int = 3
    ) -> T | None:
        """根据主键查询记录，支持重试

        Args:
            primary_key: 主键值
            retry_count: 重试次数，默认3次

        Returns:
            T | None: 查询到的记录，未找到返回None

        Raises:
            Exception: 重试后仍然失败时抛出最后一次的异常
        """
        for attempt in range(retry_count):
            try:
                result = self.search_by_primary_key(primary_key)
                return result
            except Exception as e:
                if attempt == retry_count - 1:
                    raise e
                continue
        return None
