#!/usr/bin/env python
# -*-coding:utf-8 -*-

import logging
from backoff.common.task_entity import ProcModeType
from pebble import ProcessPool, ThreadPool

logger = logging.getLogger()


class BackoffThreadPool:
    """线程池/进程池管理器"""

    def __init__(self, max_workers: int, proc_mode, timeout):
        """
        初始化执行器管理器

        Args:
            max_workers: 最大工作线程/进程数
            proc_mode: 执行器类型 (THREAD 或 PROCESS)
        """
        self.proc_mode = proc_mode
        self.max_workers = max_workers
        self.timeout = timeout

        # 根据类型创建对应的执行器
        if proc_mode == ProcModeType.THREAD.value:
            # I/O密集型任务用线程池
            self.executor = ThreadPool(max_workers=max_workers)
        elif proc_mode == ProcModeType.PROCESS.value:
            # CPU密集型任务用进程池
            self.executor = ProcessPool(max_workers=max_workers)
        else:
            raise Exception(f"不支持的执行器类型:{proc_mode}")

        logger.info(
            f"backoff_threadpool 初始化完成: proc_mode: {self.proc_mode}, max_workers: {self.max_workers}, timeout: {self.timeout}s"
        )

    def submit_task(self, func, *args, **kwargs):
        """
        提交任务到执行器

        Args:
            func: 要执行的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数

        Returns:
            Future: Pebble Future 对象，可用于获取结果或添加回调

        注意:
            - 任务会在 self.timeout 秒后超时
            - 可以通过返回的 Future 对象添加回调或获取结果
        """
        if self.proc_mode == ProcModeType.THREAD.value:
            future = self.executor.schedule(func, args=args, kwargs=kwargs)
        else:
            future = self.executor.schedule(
                func, args=args, kwargs=kwargs, timeout=self.timeout
            )

        return future

    def is_process_model(self):
        """是否为process进程模型"""
        return self.proc_mode == ProcModeType.PROCESS.value

    def shutdown(self):
        """关闭执行器"""
        self.executor.close()
        self.executor.join()
        logger.debug(f"{self.proc_mode}池关闭...")
