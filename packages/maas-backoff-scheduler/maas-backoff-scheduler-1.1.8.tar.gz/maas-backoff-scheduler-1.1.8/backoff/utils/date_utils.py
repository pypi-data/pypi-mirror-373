#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional


class DateUtils:
    """日期时间工具类，提供时间戳与格式化时间的转换功能"""
    
    @staticmethod
    def format_timestamp(
        timestamp: int, 
        fmt: str = "%Y-%m-%d %H:%M:%S", 
        is_utc: bool = False
    ) -> Optional[str]:
        """
        将时间戳转换为指定格式的时间字符串
        
        参数:
            timestamp: 时间戳（秒级）
            fmt: 时间格式字符串，默认 "%Y-%m-%d %H:%M:%S"
            is_utc: 是否使用UTC时间，默认False（本地时间）
        
        返回:
            格式化的时间字符串，转换失败返回None
        """
        try:
            if is_utc:
                # 转换为UTC时间
                dt_obj = datetime.utcfromtimestamp(timestamp)
            else:
                # 转换为本地时间
                dt_obj = datetime.fromtimestamp(timestamp)
            return dt_obj.strftime(fmt)
        except Exception as e:
            print(f"时间戳转换失败: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    # 测试时间戳
    test_timestamp = 1756180646
    
    # 转换为本地时间（默认格式）
    local_time = DateUtils.format_timestamp(test_timestamp)
    print(f"本地时间: {local_time}")  # 输出: 2025-08-26 11:57:26
    
    # 转换为UTC时间
    utc_time = DateUtils.format_timestamp(test_timestamp, is_utc=True)
    print(f"UTC时间: {utc_time}")  # 输出: 2025-08-26 03:57:26
    
    # 自定义格式
    custom_time = DateUtils.format_timestamp(test_timestamp, fmt="%Y年%m月%d日 %H时%M分%S秒")
    print(f"自定义格式: {custom_time}")  # 输出: 2025年08月26日 11时57分26秒