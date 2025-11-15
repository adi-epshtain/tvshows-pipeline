from app.redis_client import redis_client


async def init_status(request_id: str):
    await redis_client.hset(f"pipeline:{request_id}", mapping={
        "running": "true",
        "step": "starting",
        "progress": "0",
        "error": ""
    })


async def update_status(request_id: str, step: str, progress: int):
    await redis_client.hset(
        f"pipeline:{request_id}",
        mapping={
            "running": "true",
            "step": step,
            "progress": str(progress),
            "error": ""
        }
    )


async def set_error(request_id: str, error: str):
    await redis_client.hset(
        f"pipeline:{request_id}",
        mapping={
            "running": "false",
            "error": error
        }
    )
