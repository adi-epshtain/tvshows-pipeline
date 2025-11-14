import os
from fastapi import APIRouter, Query, HTTPException
import aiosqlite
from app.db import init_db, DB_PATH, create_top_shows_table, \
    create_top_shows_cast_table


router = APIRouter(prefix="/shows", tags=["Shows"])


async def ensure_db_initialized():
    if not os.path.exists(DB_PATH):
        await init_db()
        await create_top_shows_table()
        await create_top_shows_cast_table()


@router.get("/top_shows")
async def get_top_shows(limit: int = Query(10, ge=1, le=10)):
    """Return top N shows (if table exists)."""
    await ensure_db_initialized()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            res = await db.execute_fetchall(
                "SELECT id, name, rating_average, premiered FROM Top_Shows LIMIT ?",
                (limit,),
            )
        if not res:
            return {"message": "No top shows found. Run /update_shows first."}
        return [
            {"id": r[0], "name": r[1], "rating": r[2], "premiered": r[3]} for r in res
        ]
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Failed to fetch top shows: {str(e)}")


@router.get("/top_shows_multi_char_actors")
async def multi_char_actors():
    """Return actors who played more than one character"""
    await ensure_db_initialized()
    try:
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

        if not rows:
            return {"message": "No multi-character actors found or data not loaded yet."}

        return [{"person_name": r[0], "character_count": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch actors: {str(e)}")
