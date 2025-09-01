#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GPUtil
import logging

logger = logging.getLogger()


class GPUUtils:
    """
    GPU工具类，用于获取本机GPU相关信息
    """

    def __init__(self):
        
        self.has_nvidia_gpu = False
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                self.has_nvidia_gpu = True
                logger.debug(f"成功初始化NVIDIA GPU工具，检测到{len(gpus)}个GPU")
            else:
                logger.debug("成功初始化NVIDIA GPU工具，但未检测到NVIDIA GPU")
        except Exception as e:
            logger.error(f"初始化NVIDIA GPU工具失败: {str(e)}")

    def check_gpu_requirements(
        self, required_memory: float = None, max_utilization: float = None
    ) -> bool:
        """
        同时检查显存和利用率要求
        只要有一个GPU同时满足显存和利用率要求即可

        Args:
            required_memory: 需要的最小显存大小(GB)
            max_utilization: 最大允许的GPU利用率(%)

        Returns:
            Dict: 包含是否满足要求的信息
        """
        try:
            logger.debug(f"检查GPU要求: required_memory: {required_memory}GB, max_utilization: {max_utilization}%")
            if not required_memory and not max_utilization:
                return True

            # 检查是否有NVIDIA GPU
            gpus = GPUtil.getGPUs()
            if not gpus:
                logger.info("未检测到NVIDIA GPU")
                return False
            else:
                logger.info(f"检测到{len(gpus)}个NVIDIA GPU")
                
            # 找出同满足显存和利用率要求的GPU
            suitable_gpus = []
            if required_memory is not None and max_utilization is not None:
                suitable_gpus = [
                    gpu
                    for gpu in gpus
                    if gpu.memoryFree >= required_memory
                    and gpu.load * 100 <= max_utilization
                ]
            elif required_memory is not None and max_utilization is None:
                suitable_gpus = [
                    gpu for gpu in gpus if gpu.memoryFree >= required_memory
                ]
            elif max_utilization is not None and required_memory is None:
                suitable_gpus = [
                    gpu for gpu in gpus if gpu.load * 100 <= max_utilization
                ]

            if not suitable_gpus:
                logger.info("没有找到满足条件的GPU")
                return False

            # 显示满足条件的GPU信息
            if suitable_gpus:
                for gpu in suitable_gpus:
                    logger.info(
                        f"满足条件的GPU: {gpu.name} (ID: {gpu.id})\n"
                        f"显存状态: 可用 {gpu.memoryFree:.2f}GB / 总 {gpu.memoryTotal:.2f}GB\n"
                        f"当前利用率: {gpu.load * 100:.2f}%"
                    )
            return True

        except Exception as e:
            logger.error(f"检查GPU要求失败: {str(e)}")
            return False


_gpu_utils_instance = None


def get_gpu_utils() -> GPUUtils:
    global _gpu_utils_instance
    if _gpu_utils_instance is None:
        _gpu_utils_instance = GPUUtils()
    return _gpu_utils_instance
