#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .task_entity import BackoffType, ProcModeType, logger
from enum import Enum
from typing import Optional, Any


class StorageType(Enum):
    """任务状态枚举"""

    REDIS = "redis"
    MYSQL = "mysql"
    DAMENG = "dameng"


@dataclass
class StorageConfig:
    """存储配置"""

    type: str = ""  # 存储类型：redis、mysql、dameng等
    host: str = ""
    port: int = 6379
    password: Optional[str] = None
    username: Optional[str] = None
    charset: str = "utf8mb4"
    database: Optional[str] = None

    @classmethod
    def from_dict(cls, config_dict: dict):
        storage_type = config_dict.get("type", StorageType.REDIS.value)

        config = {
            "type": storage_type,
            "host": config_dict.get("host"),
            "password": config_dict.get("password"),
        }

        # 根据存储类型设置特定配置
        if storage_type == StorageType.REDIS.value:
            config.update(
                {
                    "port": config_dict.get("port", 6379),
                    "database": config_dict.get("database", 0),
                }
            )
        elif storage_type == StorageType.MYSQL.value:
            config.update(
                {
                    "port": config_dict.get("port", 3306),
                    "username": config_dict.get("username"),
                    "database": config_dict.get(
                        "database",
                    ),
                    "charset": config_dict.get("charset", "utf8mb4"),
                }
            )

        return cls(**config)

    def get_connection_info(self):
        """获取连接信息"""
        if self.type == StorageType.REDIS.value:
            return {
                "host": self.host,
                "port": self.port,
                "db": self.database,
                "password": self.password,
            }
        elif self.type == StorageType.MYSQL.value:
            return {
                "host": self.host,
                "port": self.port,
                "user": self.username,
                "password": self.password,
                "database": self.database,
                "charset": self.charset,
            }
        else:
            raise ValueError(f"不支持的存储类型: {self.type}")


@dataclass
class TaskConfig:
    """任务配置"""

    biz_prefix: str = ""  # 业务redis队列的前缀
    batch_size: int = 100  # 批量处理数量
    max_retry_count: int = 3 # 重试配置
    backoff_strategy: str = BackoffType.EXPONENTIAL.value  # fixed、linear、exponential
    backoff_interval: int = 10  # 基础间隔时间(秒)
    backoff_multiplier: float = 2.0  # 退避倍数
    min_gpu_memory_gb: int = 0  # 最小显存数量
    min_gpu_utilization: float = 0.0  # 最小显卡利用率

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            biz_prefix=config_dict.get("biz_prefix"),
            batch_size=config_dict.get("batch_size"),
            max_retry_count=config_dict.get("max_retry_count"),
            backoff_strategy=config_dict.get("backoff_strategy"),
            backoff_interval=config_dict.get("backoff_interval"),
            backoff_multiplier=config_dict.get("backoff_multiplier"),
            min_gpu_memory_gb=config_dict.get("min_gpu_memory_gb"),
            min_gpu_utilization=config_dict.get("min_gpu_utilization"),
        )


@dataclass
class ThreadPoolConfig:
    """线程池配置"""

    concurrency: int = 10
    proc_mode: str = ProcModeType.PROCESS.value  # thread、process
    exec_timeout: int = 300  # 任务超时时间(秒)

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            concurrency=config_dict.get("concurrency"),
            proc_mode=config_dict.get("proc_mode"),
            exec_timeout=config_dict.get("exec_timeout"),
        )


@dataclass
class SchedulerConfig:
    """调度器配置"""

    cron: Optional[str] = None  # cron表达式
    interval: int = 10  # 间隔时间(秒)

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(cron=config_dict.get("cron"), interval=config_dict.get("interval"))


@dataclass
class TaskBackoffConfig:
    """任务退避框架配置"""

    storage: StorageConfig = field(default_factory=StorageConfig)
    task: TaskConfig = field(default_factory=TaskConfig)
    threadpool: ThreadPoolConfig = field(default_factory=ThreadPoolConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TaskBackoffConfig":
        """从字典创建配置"""
        storage_config = StorageConfig.from_dict(config_dict.get("storage", {}))
        task_config = TaskConfig.from_dict(config_dict.get("task", {}))
        threadpool_config = ThreadPoolConfig.from_dict(
            config_dict.get("threadpool", {})
        )
        scheduler_config = SchedulerConfig.from_dict(config_dict.get("scheduler", {}))

        return cls(
            storage=storage_config,
            task=task_config,
            threadpool=threadpool_config,
            scheduler=scheduler_config,
        )

    def valid_field(self) -> None:
        validate_required_param(self.task.biz_prefix, "task.biz_prefix", None)
        validate_required_param(self.storage.type, "storage.type", None)
        validate_required_param(self.storage.host, "storage.host", None)
        validate_required_param(self.storage.password, "storage.password", None)
        if self.storage.type == StorageType.MYSQL:
            validate_required_param(self.storage.username, "storage.username", None)


def validate_required_param(
    value: Any, param_name: str, error_msg: Optional[str] = None
) -> None:
    """校验必填必填参数进行校验"""
    if not value or (isinstance(value, str) and not value.strip()):
        if error_msg:
            raise ValueError(error_msg)
        raise ValueError(f"参数 '{param_name}' 未配置")
