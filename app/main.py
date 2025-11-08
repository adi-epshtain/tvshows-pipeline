from fastapi import FastAPI
from app.pipeline import ingest_all_shows, compute_top_shows

app = FastAPI(title="TVMaze Pipeline")


@app.post("/update_shows")
async def update_shows(years: int = 15):
    """Trigger ingestion of all shows from TVMaze API"""
    await ingest_all_shows()

    # TODO: currently changed to 15 instead of 10 because there were no
    #  shows in the last 10 years that matched the criteria
    await compute_top_shows(years)
    return {"status": "All_Shows and Top_Shows updated"}


# This allows PyCharm 'Run' or 'Debug' to work directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
