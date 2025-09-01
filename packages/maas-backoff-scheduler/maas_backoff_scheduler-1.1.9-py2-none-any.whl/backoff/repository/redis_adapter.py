#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Redis存储适配器实现
RedisStorageAdapter 它实现了 StorageAdapter 接口中的所有方法。
"""

import logging
import time
from typing import Dict, Any, TypeVar
from backoff.common.backoff_config import StorageConfig
from backoff.models.redis_client import RedisClient
from backoff.repository.storage_adapter import (
    StorageAdapter,
    StorageType,
    StorageAdapterFactory,
)
from backoff.common.task_entity import TaskEntity


logger = logging.getLogger()

# 定义泛型类型变量
K = TypeVar("K")
V = TypeVar("V")


class RedisStorageAdapter(StorageAdapter[K, V]):
    """Redis存储适配器实现"""

    def __init__(self, biz_prefix: str, storage_config: StorageConfig):
        """
        初始化Redis存储适配器

        Args:
            config: Redis配置
        """
        super().__init__(biz_prefix, storage_config)

        # self.redis_client = get_redis_client(storage_config)
        # 为每个适配器实例创建独立的Redis客户端（不使用全局单例）
        self.redis_client = RedisClient(storage_config).get_client()

    def initialize(self) -> bool:
        """初始化Redis连接"""
        return True

    def close(self) -> None:
        """关闭Redis连接"""
        self.redis_client.close()
        logger.debug("Redis连接已关闭")

    def exists(self, task_id: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.redis_client.exists(self._get_task_key(task_id)))
        except Exception as e:
            logger.error(f"Redis exists操作失败: {str(e)}")
            return False

    def save_task(self, task_id: str, task_entity: Dict[str, str]) -> bool:
        """保存task任务"""
        try:
            current_time = int(time.time())
            # 保存task实体到Redis
            self.redis_client.hset(self._get_task_key(task_id), mapping=task_entity)

            # 将任务ID添加到待处理队列，使用时间戳作为权重
            self.redis_client.zadd(
                self.pending_queue_key, {task_entity["task_id"]: current_time}
            )
            return True
        except Exception as e:
            logger.error(f"Redis set操作失败: {str(e)}")
            return False

    def updata_task(self, task_id: str, task_entity: TaskEntity) -> bool:
        """更新单个task"""
        try:
            task_entity.update_time = int(time.time())
            task_data = task_entity.to_redis_dict()
            self.redis_client.hset(self._get_task_key(task_id), mapping=task_data)
            return True

        except Exception as e:
            logger.error(f"更新任务失败: [{task_id}], 错误: {str(e)}")
            return False

    def batch_fetch_pending_tasks(self, batch_size: int) -> Any:
        """批量获取待处理任务"""
        result = None
        try:
            task_ids_with_scores = self.redis_client.zrange(
                self.pending_queue_key, 0, batch_size - 1, withscores=True
            )
            return task_ids_with_scores
        except Exception as e:
            logger.error(f"Redis 批量获取待处理任务失败: {str(e)}")
            return result

    def fetch_task_details(self, task_id: str) -> Any:
        """获取单个task任务详情"""
        try:
            task_data = self.redis_client.hgetall(self._get_task_key(task_id))
            if not task_data:
                return None
            return TaskEntity.from_redis_dict(task_data)
        except Exception as e:
            logger.error(f"获取单个task任务失败: [{task_id}], 错误: {str(e)}")
            return None

    def test_connection(self) -> bool:
        """测试Redis连接"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except Exception as e:
            logger.error(f"Redis连接测试失败: {str(e)}")
            return False

    def add_task_to_pending_queue(self, task_id: str) -> bool:
        import time
        
        return bool(
            self.redis_client.zadd(self.pending_queue_key, {task_id: time.time()})
        )

    def remove_task_from_pending_queue(self, task_id: str) -> bool:
        return bool(self.redis_client.zrem(self.pending_queue_key, task_id))

    def add_task_to_processing_queue(self, task_id: str) -> bool:
        import time

        return bool(
            self.redis_client.zadd(self.processing_queue_key, {task_id: time.time()})
        )

    def remove_task_from_processing_queue(self, task_id: str) -> bool:
        return bool(self.redis_client.zrem(self.processing_queue_key, task_id))

    def add_task_to_failed_queue(self, task_id: str) -> bool:
        import time

        return bool(
            self.redis_client.zadd(self.failed_queue_key, {task_id: time.time()})
        )

    def remove_task_from_failed_queue(self, task_id: str) -> bool:
        return bool(self.redis_client.zrem(self.failed_queue_key, task_id))

    def add_task_to_completed_queue(self, task_id: str) -> bool:
        import time

        return bool(
            self.redis_client.zadd(self.completed_queue_key, {task_id: time.time()})
        )

    def remove_task_from_completed_queue(self, task_id: str) -> bool:
        return bool(self.redis_client.zrem(self.completed_queue_key, task_id))

    def queue_length(self, queue_key: str) -> int:
        return self.redis_client.zcard(queue_key)


# 注册Redis存储适配器
StorageAdapterFactory.register_adapter(StorageType.REDIS, RedisStorageAdapter)
