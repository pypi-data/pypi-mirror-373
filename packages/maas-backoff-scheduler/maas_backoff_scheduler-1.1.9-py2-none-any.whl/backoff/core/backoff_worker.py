#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务工作器模块
"""
import logging
from concurrent.futures import TimeoutError as FutureTimeoutError
from math import log
from typing import Optional, Dict, Any, Callable
from backoff.common.task_entity import TaskEntity,TaskStatus
from .task_repository import TaskRepository
from backoff.models.backoff_threadpool import BackoffThreadPool
from backoff.common.result_entity import ResultEntity
from backoff.common.error_code import ErrorCode
from backoff.utils.gpu_utils import get_gpu_utils
from backoff.utils.serialize_data_utils import dumps_data, load_parse_params
from backoff.common.backoff_config import StorageConfig
from backoff.models.redis_lock import acquire_lock, release_lock, RedisDistributedLock

logger = logging.getLogger()


def execute_task(
    task_handler: Optional[Callable], task_entity: "TaskEntity"
) -> ResultEntity:
    """
    统一的任务执行函数，支持线程池和进程池。
    注意：禁止在子进程内访问不可序列化的状态（如锁、连接等）。
    """
    task_id = task_entity.task_id
    try:
        # 执行任务
        if not task_handler:
            raise ValueError("custom_task_handler 任务处理函数未设置")

        result_obj = task_handler(task_entity)
        logger.info(f"任务 [{task_id}] 执行, 结果: {result_obj.success}")
        
        return result_obj

    except Exception as e:
        error_msg = f"execute_task 任务执行失败: {str(e)}"
        logger.error(f"任务 [{task_id}] , {error_msg}")
        return ResultEntity.fail(
            ErrorCode.TASK_EXECUTE_FAILURE.code, error_msg, None, task_id
        )


class BackoffWorker:
    """任务工作器，负责执行具体的任务"""

    def __init__(
        self,
        task_repository: TaskRepository,
        backoff_threadpool: Optional[BackoffThreadPool] = None,
        task_handler: Optional[Callable] = None,
        task_exception_handler: Optional[Callable] = None,
        task_timeout: int = 300,
    ):
        """
        初始化任务工作器

        Args:
            task_repository: 任务管理器
            backoff_threadpool: 线程池管理器
            task_handler: 任务处理函数
            task_timeout: 任务超时时间(秒)
        """
        self.task_repository = task_repository
        self.backoff_threadpool = backoff_threadpool
        self.task_handler = task_handler
        self.task_exception_handler = task_exception_handler
        self.task_timeout = task_timeout
        self.gpu_utils = get_gpu_utils()

    def execute_batch_tasks(self, pending_task_ids: list[str]) -> None:
        """
        批量执行任务

        Args:
            tasks: 任务列表

        Returns:
            list[Dict[str, Any]]: 执行结果列表
        """
        if not self.backoff_threadpool:
            logger.warning("执行任务未初始化线程池")
            return

        futures = []
        locks_by_task_id: dict[str, RedisDistributedLock] = {}

        for task_id in pending_task_ids:

            task_entity = self.task_repository.get_task(task_id)
            if not task_entity:
                continue

            valid_status = self.valid_task(task_entity)
            if valid_status == False:
                continue

            lock_key = f"{task_entity.biz_prefix}:lock:{task_id}"
            lock = acquire_lock(lock_key, blocking=False)

            if lock:
                locks_by_task_id[task_id] = lock
                # 统一标记为处理中
                self.task_repository.mark_task_processing(task_id)

                future = self.backoff_threadpool.submit_task(
                    execute_task, self.task_handler, task_entity
                )

                futures.append((task_entity, future))

        # 收集结果
        for task_entity, future in futures:

            task_id = task_entity.task_id
            lock = locks_by_task_id.get(task_id)
            try:
                # 进程模型：依赖进程池 schedule 的超时以确保超时后终止子进程
                if self.backoff_threadpool.is_process_model():
                    result = future.result()
                else:
                    # 线程模型：使用本地超时控制
                    result = future.result(timeout=self.task_timeout)
                # 统一处理结果
                if result.success:
                    result_str = dumps_data(result.result)
                    self.task_repository.mark_task_completed(task_id, result_str)
                else:
                    result_str = dumps_data(result.message) + dumps_data(result.result)
                    self.task_repository.mark_task_failed(task_id, result_str)

            except Exception as e:
                error_message = f"任务 [{task_id}] 执行异常: {str(e)}"
                if isinstance(e, FutureTimeoutError):
                    error_message = f"任务 [{task_id}] 执行超时 {self.task_timeout} 秒, 异常: {str(e)}"
                logger.error(error_message)

                # 尝试取消任务
                try:
                    if not future.done():
                        future.cancel()
                        logger.warning(f"任务 [{task_id}] 已被取消")
                except Exception as cancel_error:
                    logger.warning(f"取消任务 [{task_id}] 失败: {cancel_error}")

                # 异常时标记失败，并触发异常处理器
                self.task_repository.mark_task_failed(task_id, error_message)

                if self.task_exception_handler:
                    self.execute_exception_handler(task_entity)
            finally:
                # task异常或者有了执行结果在释放锁
                if lock:
                    release_lock(lock)
                    locks_by_task_id.pop(task_id, None)

    def valid_task(self, task_entity: TaskEntity) -> bool:
        """
        验证任务是否可以执行

        Args:
            task_entity: 任务实体

        Returns:
            bool: 是否可以执行
        """
        task_id = task_entity.task_id

        # 执行任务前先判断显存数和利用率是否满足要求,返回的是True 或者 False
        task_entity = self.task_repository.get_task(task_id)
        valid_status = self.gpu_utils.check_gpu_requirements(
            required_memory=task_entity.min_gpu_memory_gb,
            max_utilization=task_entity.min_gpu_utilization,
        )
        if valid_status == False:
            logger.info(f"任务 [{task_id}] 跳过执行，显存数和利用率不满足要求")
            return False

        # 如果有下次执行时间则判断是否到了执行时间
        if task_entity.next_execution_time > 0:
            if task_entity.is_ready_for_execution() == False:
                logger.debug(f"任务 [{task_id}] 跳过执行，未到执行时间")
                return False

        return True

    def execute_exception_handler(self, task_entity: TaskEntity) -> Any:
        """使用自定义异常处理器执行任务"""
        try:
            return self.task_exception_handler(task_entity)
        except Exception as e:
            raise e

    def set_custom_task_handler(self, handler: Callable):
        """
        设置任务处理器

        Args:
            handler: 任务处理函数
        """
        self.task_handler = handler
        logger.info(f"custom_task_handler: [{handler.__name__}] 任务处理器已设置")

    def set_custom_task_exception_handler(self, handler: Callable):
        """
        设置任务异常处理器

        Args:
            handler: 任务异常处理函数
        """
        self.task_exception_handler = handler
        logger.info(
            f"custom_task_exception_handler: [{handler.__name__}] 任务异常处理器已设置"
        )

    def get_queue_stats(self) -> Dict[str, int]:
        return self.task_repository.get_queue_stats()
