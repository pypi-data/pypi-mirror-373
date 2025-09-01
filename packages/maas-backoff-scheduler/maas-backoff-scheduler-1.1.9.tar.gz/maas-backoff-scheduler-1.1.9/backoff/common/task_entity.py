#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务实体模块
"""

import time
import logging
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass, asdict
from backoff.scheduler import biz_task_scheduler
from backoff.utils.date_utils import DateUtils

logger = logging.getLogger()


class TaskStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class BackoffType(Enum):
    """退避策略类型"""

    FIXED = "fixed"  # 固定间隔
    LINEAR = "linear"  # 线性增长
    EXPONENTIAL = "exponential"  # 指数增长


class ProcModeType(Enum):
    """执行器类型枚举"""

    THREAD = "thread"
    PROCESS = "process"


@dataclass
class TaskEntity:
    """任务实体类"""

    task_id: str
    process: int = 0  # 进度 0-100
    status: str = TaskStatus.PENDING.value
    result: str = ""  # JSON字符串
    param: str = ""  # 任务参数JSON字符串
    retry_count: int = 0
    next_execution_time: int = 0  # 下次执行时间戳
    create_time: int = 0
    update_time: int = 0
    service_instance_id: str = ""  # 服务实例ID，用于任务隔离

    # 退避策略配置
    max_retry_count: int = 3
    backoff_strategy: str = BackoffType.EXPONENTIAL.value
    backoff_interval: int = 30  # 基础间隔时间(秒)
    backoff_multiplier: float = 2.0  # 退避倍数
    min_gpu_memory_gb: int = 0  # 最小显存数量
    min_gpu_utilization: float = 0.0  # 最小显卡利用率
    biz_prefix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def to_redis_dict(self) -> Dict[str, str]:
        """转换为Redis存储格式"""
        return {
            "task_id": self.task_id,
            "process": str(self.process),
            "status": self.status,
            "result": self.result,
            "param": self.param,
            "retry_count": str(self.retry_count),
            "next_execution_time": str(self.next_execution_time),
            "create_time": str(self.create_time),
            "update_time": str(self.update_time),
            "service_instance_id": self.service_instance_id,
            "max_retry_count": str(self.max_retry_count),
            "backoff_strategy": self.backoff_strategy,
            "backoff_interval": str(self.backoff_interval),
            "backoff_multiplier": str(self.backoff_multiplier),
            "min_gpu_memory_gb": str(self.min_gpu_memory_gb),
            "min_gpu_utilization": str(self.min_gpu_utilization),
            "biz_prefix": str(self.biz_prefix),
        }

    @classmethod
    def from_redis_dict(cls, data: Dict[str, str]) -> "TaskEntity":
        """从Redis数据创建任务实体"""
        return cls(
            task_id=data.get("task_id", ""),
            process=int(data.get("process", "0")),
            status=data.get("status", TaskStatus.PENDING.value),
            result=data.get("result", ""),
            param=data.get("param", ""),
            retry_count=int(data.get("retry_count", "0")),
            max_retry_count=int(data.get("max_retry_count", "3")),
            next_execution_time=int(data.get("next_execution_time", "0")),
            create_time=int(data.get("create_time", "0")),
            update_time=int(data.get("update_time", "0")),
            service_instance_id=data.get("service_instance_id", ""),
            backoff_strategy=data.get("backoff_strategy", BackoffType.EXPONENTIAL.value),
            backoff_interval=int(data.get("backoff_interval", "30")),
            backoff_multiplier=float(data.get("backoff_multiplier", "2.0")),
            min_gpu_memory_gb=int(data.get("min_gpu_memory_gb", "0")),
            min_gpu_utilization=float(data.get("min_gpu_utilization", "0.0")),
            biz_prefix=data.get("biz_prefix", ""),
        )

    def update_process(self, process: int):
        """更新进度"""
        self.process = max(0, min(100, process))
        self.update_time = int(time.time())

    def update_status(self, status: TaskStatus):
        """更新状态"""
        self.status = status.value
        self.update_time = int(time.time())

    def update_result(self, result: str):
        """更新结果"""
        self.result = result
        self.update_time = int(time.time())

    def increment_retry(self):
        """增加重试次数"""
        self.retry_count += 1
        self.update_time = int(time.time())

    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return self.retry_count < self.max_retry_count

    def is_ready_for_execution(self) -> bool:
        """检查是否准备好执行"""
        current_time = int(time.time())
        return (
            self.status == TaskStatus.PENDING.value
            or self.status == TaskStatus.FAILED.value
        ) and self.next_execution_time <= current_time

    def calculate_next_execution_time(self) -> int:
        """计算下次执行时间"""
        current_time = int(time.time())

        if self.backoff_strategy == BackoffType.FIXED.value:
            next_time = current_time + self.backoff_interval
        elif self.backoff_strategy == BackoffType.LINEAR.value:
            next_time = current_time + (self.backoff_interval * (self.retry_count + 1))
        elif self.backoff_strategy == BackoffType.EXPONENTIAL.value:
            next_time = current_time + int(
                self.backoff_interval * (self.backoff_multiplier**self.retry_count)
            )
        else:
            next_time = current_time + self.backoff_interval

        logger.info(
            f"任务 [{self.task_id}] 执行失败重算退避属性, 下次执行时间: {DateUtils.format_timestamp(next_time)}"
        )
        return next_time

    @classmethod
    def create(
        cls,
        task_id: str,
        param: Dict[str, Any],
        max_retry_count: int = 3,
        backoff_strategy: str = "exponential",
        backoff_interval: int = 60,
        backoff_multiplier: float = 2.0,
        service_instance_id: str = "",  # 添加服务实例ID参数
        biz_prefix: str = "",
    ) -> "TaskEntity":
        """创建任务实体"""
        import json

        return cls(
            task_id=task_id,
            param=json.dumps(param),
            max_retry_count=max_retry_count,
            backoff_strategy=backoff_strategy,
            backoff_interval=backoff_interval,
            backoff_multiplier=backoff_multiplier,
            service_instance_id=service_instance_id,  # 设置服务实例ID
            create_time=int(time.time()),
            update_time=int(time.time()),
            biz_prefix=biz_prefix,
        )
