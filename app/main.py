from fastapi import FastAPI
from app.routers.pipeline_routes import router as pipeline_router
from app.routers.shows_routes import router as shows_router

app = FastAPI(title="TVMaze Pipeline API")

app.include_router(pipeline_router)
app.include_router(shows_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
