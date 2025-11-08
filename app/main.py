from fastapi import FastAPI
from app.pipeline import ingest_all_shows

app = FastAPI(title="TVMaze Pipeline")


@app.post("/update_shows")
async def update_shows():
    """Trigger ingestion of all shows from TVMaze API"""
    await ingest_all_shows()
    return {"status": "updated"}


# This allows PyCharm 'Run' or 'Debug' to work directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
