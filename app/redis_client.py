import os
import socket

import redis.asyncio as redis
from redis import RedisError


def resolve_redis_host():
    # Try Docker host 'redis'
    try:
        socket.getaddrinfo("redis", 6379)
        return "redis"   # Docker mode
    except socket.gaierror:
        return "localhost"  # Local run


REDIS_HOST = resolve_redis_host()

# Create a global async Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)


async def check_redis_connection():
    try:
        # PING is the standard healthcheck for Redis
        pong = await redis_client.ping()
        return pong is True
    except RedisError as e:
        raise ConnectionError(f"Redis unavailable: {e}")
