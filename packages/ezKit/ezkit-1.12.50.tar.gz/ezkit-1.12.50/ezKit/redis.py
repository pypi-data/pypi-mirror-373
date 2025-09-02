"""Redis Library"""

import redis as RedisClient
from loguru import logger

from . import utils


class Redis:
    """Redis"""

    # https://redis.readthedocs.io/en/stable/_modules/redis/client.html#Redis
    # https://github.com/redis/redis-py#client-classes-redis-and-strictredis
    # redis-py 3.0 drops support for the legacy Redis client class.
    # StrictRedis has been renamed to Redis and an alias named StrictRedis is provided so that users previously using StrictRedis can continue to run unchanged.
    # redis-py 3.0 之后只有一个 Redis, StrictRedis 是 Redis 的别名
    # 这里修改以下参数: host, port, socket_timeout, socket_connect_timeout, charset
    redis = RedisClient.Redis()

    def __init__(self, target: str | dict | None = None):
        """Initiation"""
        if isinstance(target, str) and utils.isTrue(target, str):
            self.redis = RedisClient.from_url(target)
        elif isinstance(target, dict) and utils.isTrue(target, dict):
            self.redis = RedisClient.Redis(**target)
        else:
            pass

    def connect_test(self) -> bool:
        info = "Redis connect test"
        try:
            logger.info(f"{info} ......")
            self.redis.ping()
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False

    def flush(self, flushall: bool = False) -> bool:
        info = "Redis flush"
        try:
            if utils.isTrue(flushall, bool):
                logger.info(f"{info} all ......")
                self.redis.flushall()
            else:
                logger.info(f"{info} db ......")
                self.redis.flushdb()
            logger.success(f"{info} [success]")
            return True
        except Exception as e:
            logger.error(f"{info} [failed]")
            logger.exception(e)
            return False
