#!/usr/bin/env python
# -*-coding:utf-8-*-

from enum import Enum, unique
from typing import Tuple

@unique
class ErrorCode(Enum):
    """错误码枚举类"""
    SUCCESS = (200, "成功")
    INTERNAL_ERROR = (500, "服务器内部错误")
    
    # 文档转换相关错误码
    TASK_NOT_FOUND = (1001, "任务不存在")
    TASK_ALREADY_EXISTS = (1002, "任务已存在")
    TASK_EXECUTE_FAILURE = (1003, "任务执行失败")
    # 参数错误
    TASK_ID_EMPTY = (1008, "task_id不能为空")
    TASK_EXECUTED = (1009, "任务正在执行中")

    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """
        根据错误码获取错误消息
        
        Args:
            code: 错误码
            
        Returns:
            str: 错误消息
        """
        for error in cls:
            if error.code == code:
                return error.message
        return "未知错误"
    
    @classmethod
    def get_error(cls, code: int) -> Tuple[int, str]:
        """
        根据错误码获取错误码和消息
        
        Args:
            code: 错误码
            
        Returns:
            Tuple[int, str]: (错误码, 错误消息)
        """
        for error in cls:
            if error.code == code:
                return error.code, error.message
        return code, "未知错误" 