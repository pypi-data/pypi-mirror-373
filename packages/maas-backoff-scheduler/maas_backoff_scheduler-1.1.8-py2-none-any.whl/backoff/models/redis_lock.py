from math import log
import time
import uuid
import logging
import random
from typing import Optional, Callable, Union
import redis
from functools import wraps

from backoff.common.backoff_config import StorageConfig
from backoff.models.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RedisDistributedLock:
    """基于 Redis 的分布式锁（SET NX EX + Lua 原子释放）。"""

    def __init__(
        self,
        lock_name: str,
        expire_time: int = 6000,
        redis_client: Optional[redis.Redis] = None,
        config: Optional[StorageConfig] = None,
    ) -> None:
        """
        Args:
            lock_name: 锁名
            expire_time: 过期秒数，防止死锁
            redis_client: 可注入的 Redis 客户端（优先使用）
            config: 项目内的 Redis 存储配置（用于获取全局客户端）
        """
        if expire_time <= 0:
            raise ValueError("expire_time 必须为正整数")

        self.lock_name = lock_name
        self.expire_time = expire_time
        self.identifier = str(uuid.uuid4())  # 唯一标识，用于释放时校验

        if not config:
            config = StorageConfig(
                host="192.168.3.52", port=6379, database=0, password="ucap2020"
            )
            self._client: redis.Redis = redis_client or get_redis_client(config)
        else:
            self._client: redis.Redis = redis_client or get_redis_client(config)

    def acquire(
        self,
        blocking: bool = True,
        timeout: Optional[float] = None,
        base_sleep: float = 0.01,
        max_sleep: float = 0.2,
        jitter: float = 0.01,
    ) -> bool:
        """
        获取锁。

        Args:
            blocking: 是否阻塞等待
            timeout: 阻塞等待的超时时间（秒）；None 表示无限等待
            base_sleep: 重试基础间隔
            max_sleep: 重试最大间隔
            jitter: 抖动，减少惊群
        """
        if not blocking:
            return self._try_acquire()

        start = time.monotonic()
        attempt = 0
        while True:
            if self._try_acquire():
                return True

            # 到达超时则返回
            if timeout is not None and (time.monotonic() - start) >= timeout:
                return False

            # 指数退避 + 随机抖动
            sleep_s = min(max_sleep, base_sleep * (2**attempt))
            if jitter > 0:
                sleep_s += random.uniform(0, jitter)
            time.sleep(sleep_s)
            attempt += 1

    def _try_acquire(self) -> bool:
        """尝试获取锁（一次）。"""
        try:
            result = self._client.set(
                name=self.lock_name,
                value=self.identifier,
                ex=self.expire_time,
                nx=True,
            )
            return bool(result is True)
        except Exception as e:
            logger.error(f"获取分布式锁失败 key={self.lock_name}, error={e}")
            return False

    def release(self) -> bool:
        """释放锁（仅持有者可释放，Lua 保证原子性）。"""
        lua_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        try:
            result = self._client.eval(lua_script, 1, self.lock_name, self.identifier)
            return bool(result == 1)
        except Exception as e:
            logger.error(f"释放分布式锁失败 key={self.lock_name}, error={e}")
            return False

    def __enter__(self) -> "RedisDistributedLock":
        self.acquire(blocking=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


LockNameType = Union[str, Callable[..., str]]


def _resolve_lock_name(lock_name: LockNameType, *args, **kwargs) -> str:
    if callable(lock_name):
        return lock_name(*args, **kwargs)
    # 支持简单模板：当存在 {key} 占位符时，用 kwargs 格式化
    if isinstance(lock_name, str) and "{" in lock_name and "}" in lock_name:
        try:
            return lock_name.format(**kwargs)
        except Exception:
            # 回退为原始字符串
            return lock_name
    return lock_name  # type: ignore[return-value]


def distributed_lock(
    lock_name: LockNameType,
    expire_time: int = 600,
    config: Optional[StorageConfig] = None,
):
    """
    分布式锁装饰器，支持：
    - lock_name 为固定字符串、可调用函数、或包含 {kw} 的模板字符串
    - 通过 config 注入项目统一 Redis 客户端
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = _resolve_lock_name(lock_name, *args, **kwargs)
            lock = RedisDistributedLock(
                lock_name=name, expire_time=expire_time, config=config
            )
            with lock:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def acquire_lock(
    key: str,
    ttl_seconds: int = 3600,
    blocking: bool = False,
    blocking_timeout: Optional[float] = None,
    config: Optional[StorageConfig] = None,
) -> Optional[RedisDistributedLock]:
    """便捷方法：获取锁，成功返回锁对象，否则返回 None。"""
    lock = RedisDistributedLock(lock_name=key, expire_time=ttl_seconds, config=config)
    ok = lock.acquire(blocking=blocking, timeout=blocking_timeout)
    return lock if ok else None


def release_lock(lock: RedisDistributedLock) -> bool:
    """便捷方法：释放锁，返回是否成功。"""
    return lock.release()


__all__ = [
    "RedisDistributedLock",
    "distributed_lock",
    "acquire_lock",
    "release_lock",
]
