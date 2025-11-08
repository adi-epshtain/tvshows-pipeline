from datetime import datetime
import aiosqlite
from app.db import DB_PATH, init_db, create_top_shows_table
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


async def compute_top_shows(years: int = 10):
    """Compute top 10 English Action shows from the last N years."""
    await create_top_shows_table()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM Top_Shows")
        processed_at = datetime.utcnow().isoformat()

        # Use f-string so {years} will be dynamically inserted
        query = f"""
        INSERT INTO Top_Shows (id, name, language, genres, premiered, rating_average, processed_at)
        SELECT id, name, language, genres, premiered, rating_average, ?
        FROM All_Shows
        WHERE language='English'
          AND genres LIKE '%Action%'
          AND premiered IS NOT NULL
          AND substr(premiered, 1, 4) >= strftime('%Y', 'now', '-{years} years')
        ORDER BY rating_average DESC
        LIMIT 10
        """
        await db.execute(query, (processed_at,))
        await db.commit()

