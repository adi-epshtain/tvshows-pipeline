from datetime import datetime
import aiosqlite
from app.db import DB_PATH, init_db
from app.api_client import fetch_all_shows


async def ingest_all_shows():
    """Fetch all shows from API and insert into SQLite."""
    await init_db()
    shows = await fetch_all_shows()
    processed_at = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        for show in shows:
            await db.execute("""
                INSERT OR REPLACE INTO All_Shows 
                (id, name, type, language, genres, status, premiered, ended,
                 rating_average, summary, updated, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                show.get("id"),
                show.get("name"),
                show.get("type"),
                show.get("language"),
                ",".join(show.get("genres", [])),
                show.get("status"),
                show.get("premiered"),
                show.get("ended"),
                (show.get("rating") or {}).get("average"),
                show.get("summary"),
                show.get("updated"),
                processed_at
            ))
        await db.commit()
