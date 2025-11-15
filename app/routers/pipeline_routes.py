import hashlib
import json
import uuid

from fastapi import APIRouter, BackgroundTasks, status, Query, Header, Response
from app.pipeline import run_full_pipeline
from app.pipeline_status import init_status
from app.redis_client import redis_client

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])
default_header = Header(default=None, convert_underscores=False)


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_shows(background_tasks: BackgroundTasks,
                       years: int = Query(10, ge=0)):
    # 1) generate request_id
    request_id = str(uuid.uuid4())

    # 2) initialize state in Redis
    await init_status(request_id)

    # 3) get initial state from Redis
    initial_state = await redis_client.hgetall(f"pipeline:{request_id}")

    # 4) compute initial signature
    signature = make_signature(initial_state)

    # 5) pass it to the background pipeline
    background_tasks.add_task(run_full_pipeline, request_id, years)

    return {"status": "accepted",
            "request_id": request_id,
            "signature": signature,
            "message": f"Pipeline started for {years} years"}


def make_signature(data: dict) -> str:
    raw: str = json.dumps(data, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


@router.get(
    "/status/{request_id}",
    responses={
        200: {"description": "Status returned"},
        204: {"description": "No changes since last poll"},
        404: {"description": "request_id not found"},
    }
)
async def get_status(request_id: str,
                     previous_signature: str | None = default_header):
    data: dict = await redis_client.hgetall(f"pipeline:{request_id}")

    if not data:
        return Response(status_code=404)

    signature: str = make_signature(data)

    if previous_signature == signature:
        return Response(status_code=204)

    return {
        "status": data,
        "signature": signature
    }
