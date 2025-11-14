from fastapi import APIRouter, BackgroundTasks, status, Query

from app.pipeline import run_full_pipeline
from app.pipeline_status import pipeline_status

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_shows(background_tasks: BackgroundTasks,
                       years: int = Query(10, ge=0)):
    background_tasks.add_task(run_full_pipeline, years)
    return {"status": "accepted", "message": f"Pipeline started for {years} years"}


@router.get("/status")
async def get_status():
    return pipeline_status.to_dict()
