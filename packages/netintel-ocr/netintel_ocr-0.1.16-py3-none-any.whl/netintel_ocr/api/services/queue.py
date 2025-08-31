"""
Queue Service - Redis queue management
"""

import os
import redis.asyncio as redis
from typing import Optional
import json

_redis_client: Optional[redis.Redis] = None

async def init_queue():
    """Initialize Redis queue connection"""
    global _redis_client
    
    # Get configuration from environment
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Create Redis client
    _redis_client = await redis.from_url(redis_url, decode_responses=True)
    
    # Test connection
    await _redis_client.ping()
    
    print(f"Connected to Redis at {redis_url}")

async def check_queue_connection() -> bool:
    """Check if queue is connected"""
    if not _redis_client:
        return False
    
    try:
        await _redis_client.ping()
        return True
    except:
        return False

def get_queue() -> redis.Redis:
    """Get queue client"""
    if not _redis_client:
        raise RuntimeError("Queue not initialized")
    return _redis_client

async def enqueue_job(queue_name: str, job_data: dict) -> str:
    """Add job to queue"""
    client = get_queue()
    job_json = json.dumps(job_data)
    await client.lpush(queue_name, job_json)
    return job_data.get("job_id")

async def dequeue_job(queue_name: str, timeout: int = 0) -> Optional[dict]:
    """Get job from queue"""
    client = get_queue()
    result = await client.brpop(queue_name, timeout=timeout)
    if result:
        _, job_json = result
        return json.loads(job_json)
    return None