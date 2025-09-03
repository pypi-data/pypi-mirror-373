import json
from typing import Dict, List, Optional
import redis.asyncio as redis
from Osdental.Exception.ControlledException import RedisException
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Constant import Constant

class RedisCacheAsync:

    _instances: Dict[str, 'RedisCacheAsync'] = {}

    def __new__(cls, redis_url:str):
        if redis_url not in cls._instances:
            cls._instances[redis_url] = super(RedisCacheAsync, cls).__new__(cls)
        return cls._instances[redis_url]

    def __init__(self, redis_url:str):
        """Connect to the Redis server."""
        if not hasattr(self, 'initialized'):
            self.pool = redis.ConnectionPool.from_url(redis_url)
            self.client = redis.Redis(connection_pool=self.pool)
            self.initialized = True


    async def set_dict(self, key:str, value:Dict[str,str], ttl:Optional[int] = None):
        """Set a JSON value in the cache."""
        try:
            json_value = json.dumps(value)
            await self.client.set(key, json_value)
            if ttl:
                await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f'Redis set_dict error: {str(e)}')
            raise RedisException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))

    async def set_str(self, key:str, value:str, ttl:Optional[int] = None):
        """Set a string value in the cache."""
        try:
            await self.client.set(key, value)
            if ttl:
                await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f'Redis set_str error: {str(e)}')
            raise RedisException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))

    async def get_dict(self, key:str) -> Optional[str]:
        """Get a JSON value from the cache and convert it back to a Python object."""
        try:
            json_value = await self.client.get(key)
            if json_value:
                return json.loads(json_value)
            return None
        except Exception as e:
            logger.error(f'Redis get_dict error: {str(e)}')
            raise RedisException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))


    async def get_str(self, key:str) -> Optional[str]:
        """Get a string value from the cache."""
        try:
            value = await self.client.get(key)
            return value.decode(Constant.DEFAULT_ENCODING) if value else None
        except Exception as e:
            logger.error(f'Redis get_str error: {str(e)}')
            raise RedisException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))

    async def delete(self, key:str) -> bool:
        """Delete a value from the cache."""
        try:
            return await self.client.delete(key)
        except Exception as e:
            logger.error(f'Redis delete error: {str(e)}')
            raise RedisException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))

    async def exists(self, key:str) -> bool:
        """Check if a key exists in the cache."""
        return await self.client.exists(key)

    async def flush(self):
        """Flush all keys in the cache."""
        await self.client.flushdb()
    
    async def flush_all(self):
        """Flush all keys in all Redis databases."""
        await self.client.flushall()

    async def mget(self, keys:List[str]) -> List[Optional[str]]:
        """Get multiple values from the cache."""
        values = await self.client.mget(keys)
        return [json.loads(value) if value else None for value in values]

    async def clear_cache(self, prefix: str):
        """Delete all keys matching the given prefix."""
        async for key in self._scan_keys(match=f'{prefix}*'):
            await self.client.delete(key)

    async def _scan_keys(self, match: str = '*'):
        """Asynchronous generator to scan keys matching a pattern."""
        async for key in self.client.scan_iter(match=match):
            yield key

    async def close(self):
        """Close the connection pool and Redis client."""
        if self.client:
            await self.client.close()  
        if self.pool:
            await self.pool.disconnect(inuse_connections=True) 
