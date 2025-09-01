#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存储适配器模块

提供统一的存储接口，支持不同类型的存储实现（Redis、MySQL、达梦DB等）
"""
import abc
import logging
import enum
from typing import List, Any, TypeVar, Generic
from backoff.common.backoff_config import StorageConfig

logger = logging.getLogger()


K = TypeVar("K")
V = TypeVar("V")


class StorageType(enum.Enum):
    """存储类型枚举"""

    REDIS = "redis"
    MYSQL = "mysql"

    @classmethod
    def get_enum_by_value(cls, value: str) -> "StorageType":
        return cls(value)


class StorageAdapter(Generic[K, V], abc.ABC):
    """存储适配器抽象基类"""

    def __init__(self, biz_prefix: str, config: StorageConfig):
        """
        初始化存储适配器

        Args:
            config: 存储配置
        """
        self.config = config
        self._initialized = False
        self.biz_prefix = biz_prefix
        self.task_key_prefix = f"{biz_prefix}:task:"
        self.pending_queue_key = f"{biz_prefix}:pending_queue"
        self.processing_queue_key = f"{biz_prefix}:processing_queue"
        self.failed_queue_key = f"{biz_prefix}:failed_queue"
        self.completed_queue_key = f"{biz_prefix}:completed_queue"

    def _get_task_key(self, task_id: str) -> str:
        """获取任务在Redis中的key"""
        return f"{self.task_key_prefix}{task_id}"

    @abc.abstractmethod
    def initialize(self) -> bool:
        """初始化存储连接"""
        pass

    @abc.abstractmethod
    def close(self) -> None:
        """关闭存储连接"""
        pass

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass

    @abc.abstractmethod
    def save_task(self, key: str, task: Any) -> bool:
        """保存task任务"""
        pass

    @abc.abstractmethod
    def updata_task(self, key: str, task: Any) -> bool:
        """更新task任务"""
        pass

    @abc.abstractmethod
    def batch_fetch_pending_tasks(self, batch_size: int) -> Any:
        """批量获取待处理任务"""
        pass

    @abc.abstractmethod
    def fetch_task_details(self, task_id: str) -> Any:
        """获取单个task任务详情"""
        pass
    

    @abc.abstractmethod
    def test_connection(self) -> bool:
        """测试存储连接是否可用"""
        pass

    @abc.abstractmethod
    def add_task_to_pending_queue(self, task_id: str) -> bool:
        """添加task任务进入pending队列"""
        pass

    @abc.abstractmethod
    def remove_task_from_pending_queue(self, task_id: str) -> bool:
        """从pending队列移除task任务"""
        pass

    @abc.abstractmethod
    def add_task_to_processing_queue(self, task_id: str) -> bool:
        """添加task任务进入processing队列"""
        pass

    @abc.abstractmethod
    def remove_task_from_processing_queue(self, task_id: str) -> bool:
        """从processing队列移除task任务"""
        pass

    @abc.abstractmethod
    def add_task_to_failed_queue(self, task_id: str) -> bool:
        """添加task任务进入failed队列"""
        pass

    @abc.abstractmethod
    def remove_task_from_failed_queue(self, task_id: str) -> bool:
        """从failed队列移除task任务"""
        pass

    @abc.abstractmethod
    def add_task_to_completed_queue(self, task_id: str) -> bool:
        """添加task任务进入completed队列"""
        pass

    @abc.abstractmethod
    def remove_task_from_completed_queue(self, task_id: str) -> bool:
        """从completed队列移除task任务"""
        pass

    @abc.abstractmethod
    def queue_length(self, queue_key: str) -> int:
        """队列长度"""
        pass


class StorageAdapterFactory:
    """存储适配器工厂类"""

    _adapters = {}  # 存储已创建的适配器实例

    @classmethod
    def register_adapter(cls, storage_type: StorageType, adapter_class):
        """
        注册存储适配器类

        Args:
            storage_type: 存储类型
            adapter_class: 适配器类
        """
        cls._adapters[storage_type] = adapter_class
        logger.debug(
            f"已注册存储适配器: {storage_type.value} -> {adapter_class.__name__}"
        )

    @classmethod
    def create_adapter(cls, biz_prefix: str, config: StorageConfig) -> StorageAdapter:
        """
        创建存储适配器实例

        Args:
            storage_type: 存储类型
            config: 存储配置

        Returns:
            StorageAdapter: 存储适配器实例

        Raises:
            ValueError: 如果存储类型未注册
        """
        storage_type = StorageType.get_enum_by_value(config.type)
        if storage_type not in cls._adapters:
            raise ValueError(f"unregistered storage type: {storage_type.value}")

        adapter_class = cls._adapters[storage_type]
        adapter = adapter_class(biz_prefix, config)

        if not adapter.initialize():
            raise RuntimeError(f"failed to initialize the storage adapter: {storage_type.value}")

        logger.info(f"storage adapter created type: [{storage_type.value}]")
        return adapter

    @classmethod
    def get_adapter_types(cls) -> List[StorageType]:
        """
        获取所有已注册的适配器类型

        Returns:
            List[StorageType]: 适配器类型列表
        """
        return list(cls._adapters.keys())
