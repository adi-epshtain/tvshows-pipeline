from fastapi import FastAPI, Query
from app.pipeline import ingest_all_shows, compute_top_shows, \
    fetch_top_shows_cast
import aiosqlite
from app.db import DB_PATH


app = FastAPI(title="TVMaze Pipeline API")


# --------------------------------------------
# 1. Update all data from TV maze (main pipeline)
# --------------------------------------------
@app.post("/update_shows")
async def update_shows(years: int = 15):
    """Fetch all shows, compute top shows, and fetch their cast"""
    await ingest_all_shows()  # stage1

    # TODO: currently changed to 15 instead of 10 because there were no
    #  shows in the last 10 years that matched the criteria
    await compute_top_shows(years)  # stage2
    await fetch_top_shows_cast()  # stage3
    return {"status": f"Database updated for last {years} years"}


# --------------------------------------------
# 2. Return top shows (default limit 10, max 10)
# --------------------------------------------
@app.get("/top_shows")
async def get_top_shows(limit: int = Query(10, le=10)):
    """Return top N shows from Top_Shows table"""
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT id, name, rating_average, premiered" \
                " FROM Top_Shows LIMIT ?"
        rows = await db.execute_fetchall(query, (limit,))
    return [
        {"id": row[0], "name": row[1], "rating": row[2], "premiered": row[3]}
        for row in rows
    ]


# --------------------------------------------
# 3. Return actors who played multiple characters in Top_Shows
# --------------------------------------------
@app.get("/top_shows_multi_char_actors")
async def multi_char_actors():
    """Return actors who played more than one character in Top_Shows."""
    async with aiosqlite.connect(DB_PATH) as db:
        query = """
        SELECT person_name, COUNT(DISTINCT character_id) as char_count
        FROM Top_Shows_Cast
        WHERE person_name IS NOT NULL
        GROUP BY person_id
        HAVING char_count > 1
        ORDER BY char_count DESC
        """
        rows = await db.execute_fetchall(query)
    return [{"person_name": r[0], "character_count": r[1]} for r in rows]


# This allows PyCharm 'Run' or 'Debug' to work directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
