#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存储适配器包初始化文件
"""

from .storage_adapter import (
    StorageAdapter,
    StorageType,
    StorageAdapterFactory
)
from .redis_adapter import RedisStorageAdapter

__all__ = [
    'StorageAdapter',
    'StorageType',
    'StorageAdapterFactory',
    'RedisStorageAdapter',
]