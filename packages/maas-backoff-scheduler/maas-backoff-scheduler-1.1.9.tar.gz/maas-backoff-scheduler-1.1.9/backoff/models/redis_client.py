#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Redis客户端管理模块
"""
from redis.exceptions import RedisError
import redis
import logging
from typing import Optional
from backoff.common.backoff_config import StorageConfig

logger = logging.getLogger()

class RedisClient:
    """Redis客户端管理类"""

    def __init__(self, config: StorageConfig):
        """
        初始化Redis客户端

        Args:
            config: Redis配置
        """
        self.config = config
        self._client: Optional[redis.Redis] = None

    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        if self._client is None:
            try:
                # 创建连接池
                pool = redis.ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    db=self.config.database,
                    password=self.config.password,
                    decode_responses=True,
                    max_connections=10,  # 最大连接数
                    socket_timeout=5,    # 操作超时时间
                    socket_connect_timeout=5,  # 连接超时时间
                    retry_on_timeout=True,     # 超时时重试
                    health_check_interval=30   # 健康检查间隔
                )
                
                # 创建Redis客户端
                self._client = redis.Redis(
                    connection_pool=pool,
                    retry_on_timeout=True
                )
                
                # 测试连接
                self._client.ping()
                logger.info(f"Redis连接成功:{self.config.host}:{self.config.port}")
                
            except RedisError as e:
                logger.error(f"Redis连接失败: {str(e)}")
                raise

        return self._client

    def test_connection(self) -> bool:
        """测试Redis连接"""
        try:
            client = self.get_client()
            client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis连接测试失败: {str(e)}")
            return False

    def close(self):
        """关闭Redis连接"""
        if self._client:
            self._client.close()
            self._client = None
            logger.debug("Redis连接已关闭")


# 全局Redis客户端实例
_redis_client: Optional[RedisClient] = None


def create_new_redis_client(config: StorageConfig) -> RedisClient:
    """
    创建新的Redis客户端实例
    
    Args:
        config: Redis配置
        
    Returns:
        RedisClient: 新的Redis客户端实例
    """
    return RedisClient(config)


def get_redis_client(config: StorageConfig) -> redis.Redis:
    """获取Redis客户端（向后兼容，使用全局实例）"""
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(config)

    return _redis_client.get_client()


def init_redis_client(config: StorageConfig) -> bool:
    """初始化Redis客户端"""
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(config)

    return _redis_client.test_connection()


def close_redis_client():
    """关闭Redis客户端"""
    global _redis_client

    if _redis_client:
        _redis_client.close()
        _redis_client = None
