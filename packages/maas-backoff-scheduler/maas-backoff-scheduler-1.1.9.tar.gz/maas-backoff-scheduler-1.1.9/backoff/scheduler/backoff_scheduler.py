#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具API接口
"""
import logging
import uuid
from typing import Optional, Dict, Any, Callable
from backoff.common.result_entity import ResultEntity

from backoff.common.backoff_config import (
    TaskBackoffConfig,
    StorageConfig,
    BackoffType,
    ProcModeType,
    TaskConfig,
    TaskConfig,
    ThreadPoolConfig,
    SchedulerConfig,
)
from backoff.common.task_entity import TaskEntity, TaskStatus
from backoff.core.task_repository import TaskRepository
from backoff.core.backoff_worker import BackoffWorker
from backoff.models.backoff_threadpool import BackoffThreadPool
from backoff.models.redis_client import close_redis_client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from .biz_task_scheduler import task_scheduler
from backoff.common.error_code import ErrorCode

logger = logging.getLogger()

# 全局实例引用，用于任务函数访问
_scheduler_instances = {}


def _global_job_function(scheduler_id: str):
    """全局任务执行函数，可以被APScheduler序列化"""
    if scheduler_id not in _scheduler_instances:
        logger.error(f"调度器实例不存在: {scheduler_id}")
        return

    scheduler = _scheduler_instances[scheduler_id]
    if not scheduler.backoff_worker or not scheduler.task_repository:
        logger.error("任务工作器或任务管理器未初始化")
        scheduler.shutdown()
        return

    try:
        # 获取待处理任务
        pending_task_ids = scheduler.task_repository.get_pending_taskIds(
            batch_size=scheduler.config.task.batch_size
        )

        if not pending_task_ids:
            logger.debug(
                f"{scheduler.config.task.biz_prefix}_{scheduler.startup_timestamp}, 没有待处理任务"
            )
            return

        scheduler.backoff_worker.execute_batch_tasks(pending_task_ids)

    except Exception as e:
        logger.error(f"执行定时任务失败: {e}", exc_info=True)


class TaskBackoffScheduler:
    """任务退避管理工具主类"""

    def __init__(self, config: Optional[TaskBackoffConfig] = None):
        """
        初始化任务退避管理工具

        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or TaskBackoffConfig()

        # 校验参数
        self.config.valid_field()

        self.task_repository: Optional[TaskRepository] = None
        self.backoff_worker: Optional[BackoffWorker] = None
        self.backoff_threadpool: Optional[BackoffThreadPool] = None
        self._initialized = False

        # 生成唯一的启动时间戳，用于任务隔离
        self.startup_timestamp = self._generate_startup_timestamp()

        # 先完成所有初始化
        self.initialize()
        if self._initialized == False:
            raise Exception("backoff scheduler 实例未完成初始化")

        # 将实例添加到全局引用中
        _scheduler_instances[self.startup_timestamp] = self

        # 初始化完成后再启动调度器
        scheduler_name = (
            f"{self.config.task.biz_prefix}_{self.startup_timestamp}_scheduler"
        )
        self.scheduler_name = scheduler_name

        task_scheduler.add_scheduler(scheduler_name, self.default_biz_scheduler)

        logger.debug(
            f"任务退避管理工具初始化完成，启动时间戳: {self.startup_timestamp}"
        )

    def _generate_startup_timestamp(self) -> str:
        """生成唯一的启动时间戳"""
        import time
        import uuid

        # 使用格式: YYYYMMDD_HHMMSS
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        # YYYYMMDD_HHMMSS + 4位随机数
        timestamp = timestamp + "_" + str(uuid.uuid4().hex[:4])
        return timestamp

    def initialize(self) -> bool:
        """
        初始化框架

        Returns:
            bool: 是否初始化成功
        """

        try:
            # 初始化任务持久化工具
            self.task_repository = TaskRepository(
                biz_prefix=self.config.task.biz_prefix,
                storage_config=self.config.storage,
            )

            # 初始化线程池管理器
            self.backoff_threadpool = BackoffThreadPool(
                max_workers=self.config.threadpool.concurrency,
                proc_mode=self.config.threadpool.proc_mode,
                timeout=self.config.threadpool.exec_timeout,
            )

            # 初始化任务核心执行器
            self.backoff_worker = BackoffWorker(
                task_repository=self.task_repository,
                backoff_threadpool=self.backoff_threadpool,
                task_timeout=self.config.threadpool.exec_timeout,
            )
            logger.info(
                f"backoff_worker 核心执行器初始化，task_timeout: {self.config.threadpool.exec_timeout}"
            )

            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"任务退避管理工具初始化失败: {str(e)}")
            task_scheduler.stop()
            return False

    def default_biz_scheduler(self):
        """
        创建自定义的业务调度器

        Returns:
            BackgroundScheduler: 配置好的调度器实例
        """

        # 配置Redis作为jobstore，添加服务实例ID作为key前缀
        job_stores = {
            "default": RedisJobStore(
                host=self.config.storage.host,
                port=self.config.storage.port,
                db=self.config.storage.database,
                password=self.config.storage.password,
                # 使用服务实例ID作为key前缀，确保任务隔离
                jobs_key=f"{self.config.task.biz_prefix}_{self.startup_timestamp}_jobs",
                run_times_key=f"{self.config.task.biz_prefix}_{self.startup_timestamp}_run_times",
            )
        }

        # 配置线程池执行器
        executors = {"default": ThreadPoolExecutor(max_workers=10)}

        # 创建调度器
        scheduler = BackgroundScheduler(
            jobstores=job_stores,
            executors=executors,
        )

        # 添加定时任务job，使用全局函数
        scheduler.add_job(
            _global_job_function,
            "interval",
            seconds=self.config.scheduler.interval,
            args=[self.startup_timestamp],
            id=f"{self.config.task.biz_prefix}_{self.startup_timestamp}_job",
            name=f"退避工具内置调度任务_{self.startup_timestamp}",
            max_instances=3,  # 允许最多3个实例同时运行
            replace_existing=True,  # job 存在时替换
            coalesce=True,  # 是否合并任务
        )

        logger.info(
            f"backoff_scheduler 核心调度器初始化成功:  interval: [{self.config.scheduler.interval}s] "
        )
        return scheduler

    def set_custom_task_handler(self, handler: Callable):
        """
        设置业务任务处理器

        Args:
            handler: 任务处理函数，接收(task_entity, task_params)参数
        """
        if self.backoff_worker:
            self.backoff_worker.set_custom_task_handler(handler)
        else:
            logger.error("task_handler任务核心执行器未初始化")

    def set_custom_task_exception_handler(self, handler: Callable):
        """
        设置任务异常处理器

        Args:
            handler: 任务处理函数，接收(task_entity, task_params)参数
        """
        if self.backoff_worker:
            self.backoff_worker.set_custom_task_exception_handler(handler)
        else:
            logger.error("task_exception_handler任务核心执行器未初始化")

    def create_task(
        self, task_params: Dict[str, Any], task_id: Optional[str] = None
    ) -> Optional[str]:
        """
        创建任务

        Args:
            task_params: 任务参数
            task_id: 任务ID，如果为None则自动生成
            max_retry_count: 最大重试次数
            backoff_strategy: 退避类型
            backoff_interval: 退避间隔(秒)
            backoff_multiplier: 退避倍数

        Returns:
            str: 任务ID，如果创建失败返回None
        """
        if not self._initialized:
            logger.error("框架未初始化，请先调用initialize()")
            return None

        try:
            # 工具不强制校验task_id，不传则生成
            if task_id is None:
                task_id = str(uuid.uuid4())

            # 创建任务实体，添加服务实例ID
            task_entity = TaskEntity.create(
                task_id=task_id,
                param=task_params,
                max_retry_count=self.config.task.max_retry_count,
                backoff_strategy=self.config.task.backoff_strategy,
                backoff_interval=self.config.task.backoff_interval,
                backoff_multiplier=self.config.task.backoff_multiplier,
                service_instance_id=self.startup_timestamp,  # 添加服务实例ID
                biz_prefix=self.config.task.biz_prefix,
            )

            if self.task_repository.create_task(task_entity):
                return task_id
            else:
                return None

        except Exception as e:
            logger.error(f"创建任务异常: {str(e)}")
            return None

    def get_task(self, task_id: str) -> Optional[TaskEntity]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            TaskEntity: 任务实体
        """
        if self.task_repository:
            return self.task_repository.get_task(task_id)
        return None

    def delete_task(self, task_id: str) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否删除成功
        """
        if self.task_repository:
            return self.task_repository.delete_task(task_id)
        return False

    def cancel_task(self, task_id: str) -> ResultEntity:
        """
        撤销任务，
        如果任务状态pending，则取消任务，并返回True
        如果任务状态processing，则返回False

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否撤销成功
        """
        if self.task_repository:
            task_entity = self.task_repository.get_task(task_id)
            if task_entity and task_entity.status == TaskStatus.PENDING:
                flag = self.task_repository.delete_task(task_id)
                return ResultEntity.res(success=flag)
        return ResultEntity.fail(ErrorCode.TASK_EXECUTED, "任务已执行，无法撤销", "")

    def get_queue_stats(self) -> Dict[str, int]:
        """
        获取队列统计信息

        Returns:
            Dict[str, int]: 队列统计
        """
        if self.task_repository:
            return self.task_repository.get_queue_stats()
        return {}

    def shutdown(self):
        """关闭框架"""
        try:
            # 停止调度器
            if task_scheduler:
                task_scheduler.stop()

            # 关闭线程池
            if self.backoff_threadpool:
                self.backoff_threadpool.shutdown()

            # 关闭Redis连接
            close_redis_client()

            # 从全局引用中移除
            if self.startup_timestamp in _scheduler_instances:
                del _scheduler_instances[self.startup_timestamp]

            self._initialized = False

        except Exception as e:
            logger.error(f"关闭框架失败: {str(e)}")

    def start(self):
        """启动scheduler框架"""
        try:
            # 启动调度器
            if task_scheduler:
                task_scheduler.start(self.scheduler_name)

        except Exception as e:
            logger.error(f"启动scheduler框架失败: {str(e)}")

    def __enter__(self):
        """上下文管理器入口"""
        if not self.initialize():
            raise RuntimeError("框架初始化失败")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()

    def update_task_progress(self, task_id: str, progress: int) -> bool:
        """
        更新任务进度
        """
        if self.task_repository:
            return self.task_repository.update_task_progress(task_id, progress)

    def mark_task_completed(self, task_id: str, result: str = "") -> bool:
        """
        标记任务为已完成
        """
        if self.task_repository:
            return self.task_repository.mark_task_completed(task_id, result)

    def mark_task_failed(self, task_id: str, result: str = "") -> bool:
        """
        标记任务为失败
        """
        if self.task_repository:
            return self.task_repository.mark_task_failed(task_id, result)

    def mark_task_processing(self, task_id: str) -> bool:
        """
        标记任务为处理中
        """
        if self.task_repository:
            return self.task_repository.mark_task_processing(task_id)
