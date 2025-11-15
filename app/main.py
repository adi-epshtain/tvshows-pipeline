from fastapi import FastAPI
from app.redis_client import check_redis_connection
from app.routers.pipeline_routes import router as pipeline_router
from app.routers.shows_routes import router as shows_router
from app.logger import log


app = FastAPI(title="TVMaze Pipeline API")

app.include_router(pipeline_router)
app.include_router(shows_router)


@app.on_event("startup")
async def verify_redis():
    global redis_available
    try:
        ok = await check_redis_connection()
        if ok:
            redis_available = True
            log.info("Redis connection OK")
        else:
            redis_available = False
            log.error("Redis not available")
    except Exception:
        redis_available = False
        log.error("Redis not available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
