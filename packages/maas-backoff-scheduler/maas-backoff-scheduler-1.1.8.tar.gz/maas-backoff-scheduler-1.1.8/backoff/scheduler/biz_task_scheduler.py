#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging

logger = logging.getLogger()


class TaskScheduler:
    """调度器管理器"""

    _instance = None
    _schedulers = {}  # 存储多个调度器

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskScheduler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._schedulers = {}

    def add_scheduler(self, name, scheduler_func=None, **kwargs):
        """
        添加调度器

        Args:
            name: 调度器名称
            scheduler_func: 创建调度器的函数，如果为None则使用默认的create_scheduler
            **kwargs: 传递给scheduler_func的参数
        """

        if name in self._schedulers:
            logger.warning(f"调度器 [{name}] 已存在，将被覆盖")

        try:
            if scheduler_func:
                # 如果传入的是函数，则调用它获取调度器
                scheduler = scheduler_func(**kwargs)
                # 如果scheduler_func返回None，则可能是直接传入了调度器实例
                if scheduler is None and hasattr(scheduler_func, 'running'):
                    scheduler = scheduler_func
            else:
                # 如果没有传入函数，则可能直接传入了调度器实例
                scheduler = None
                
            if scheduler is None:
                raise ValueError(f"无法创建调度器: [{name}]")

            self._schedulers[name] = scheduler
            logger.debug(f"调度器 [[{name}]] 添加成功")

            return scheduler

        except Exception as e:
            logger.error(f"添加调度器 [{name}] 失败: {str(e)}")
            raise

    def start(self, scheduler_name=None):
        """
        启动调度器

        Args:
            scheduler_name: 指定启动的调度器名称，如果为None则启动所有调度器
        """
        if scheduler_name:
            # 启动指定的调度器
            if scheduler_name in self._schedulers:
                scheduler = self._schedulers[scheduler_name]
                if not scheduler.running:
                    scheduler.start()
                    logger.debug(f"调度器 {scheduler_name} 启动成功")
                else:
                    logger.warning(f"调度器 {scheduler_name} 已经在运行中")
            else:
                logger.error(f"调度器 {scheduler_name} 不存在")
        else:
            # 启动所有调度器
            for name, scheduler in self._schedulers.items():
                if not scheduler.running:
                    scheduler.start()
                    logger.debug(f"调度器 [{name}] 启动成功")
                else:
                    logger.warning(f"调度器 [{name}] 已经在运行中")

    def stop(self, scheduler_name=None):
        """
        停止调度器

        Args:
            scheduler_name: 指定停止的调度器名称，如果为None则停止所有调度器
        """
        if scheduler_name:
            # 停止指定的调度器
            if scheduler_name in self._schedulers:
                scheduler = self._schedulers[scheduler_name]
                if scheduler.running:
                    scheduler.shutdown()
                    logger.debug(f"调度器 {scheduler_name} 已停止")
                else:
                    logger.warning(f"调度器 {scheduler_name} 未在运行")
            else:
                logger.error(f"调度器 {scheduler_name} 不存在")
        else:
            # 停止所有调度器
            for name, scheduler in self._schedulers.items():
                if scheduler.running:
                    try:
                        scheduler.shutdown()
                        logger.debug(f"调度器 [{name}] 已停止")
                    except Exception as e:
                        logger.error(f"停止调度器 [{name}] 失败: {str(e)}")
                else:
                    logger.warning(f"调度器 [{name}] 未在运行")

    def get_jobs(self, scheduler_name=None):
        """
        获取所有任务

        Args:
            scheduler_name: 调度器名称，如果为None则返回所有调度器的任务
        """
        if scheduler_name:
            scheduler = self._schedulers.get(scheduler_name)
            return scheduler.get_jobs() if scheduler else []
        else:
            # 返回所有调度器的任务
            all_jobs = []
            for scheduler in self._schedulers.values():
                all_jobs.extend(scheduler.get_jobs())
            return all_jobs

    def remove_job(self, job_id, scheduler_name=None):
        """
        移除任务

        Args:
            job_id: 任务ID
            scheduler_name: 调度器名称，如果为None则从所有调度器中移除
        """
        if scheduler_name:
            scheduler = self._schedulers.get(scheduler_name)
            if scheduler:
                scheduler.remove_job(job_id)
            else:
                logger.error(f"调度器 {scheduler_name} 不存在")
        else:
            # 从所有调度器中移除任务
            for name, scheduler in self._schedulers.items():
                try:
                    scheduler.remove_job(job_id)
                    logger.debug(f"从调度器 [{name}] 中移除任务 {job_id}")
                except Exception as e:
                    logger.warning(
                        f"从调度器 [{name}] 中移除任务 {job_id} 失败: {str(e)}"
                    )

    def list_schedulers(self):
        """列出所有调度器及其状态"""
        scheduler_info = {}
        for name, scheduler in self._schedulers.items():
            logger.debug(
                f"已注册的调度器名称: [{name}] 状态: {scheduler.running}, scheduler: {scheduler.get_jobs()}"
            )
            scheduler_info[name] = {
                "running": scheduler.running,
                "job_count": len(scheduler.get_jobs()),
            }
        return scheduler_info


# 全局调度器管理器实例
task_scheduler = TaskScheduler()
