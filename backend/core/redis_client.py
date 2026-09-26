import redis.asyncio as redis

from core.config import settings

client = redis.from_url(settings.redis_url, decode_responses=True)


async def ping() -> bool:
    try:
        return bool(await client.ping())
    except redis.RedisError:
        return False
