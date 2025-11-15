from datetime import datetime, timedelta
import asyncio
import aiosqlite
import httpx
from app.api_client import fetch_all_shows, fetch_cast
from app.db import DB_PATH, init_db, create_top_shows_table, \
    create_top_shows_cast_table
from app.pipeline_status import update_status, set_error
from app.logger import log


async def run_full_pipeline(request_id: str, years: int):
    try:
        await update_status(request_id=request_id,
                            step="Fetching all shows",
                            progress=10)
        await ingest_all_shows(request_id=request_id)

        await update_status(request_id=request_id,
                            step="Computing top shows",
                            progress=40)
        await compute_top_shows(years)

        await update_status(request_id=request_id,
                            step="Fetching cast for top shows",
                            progress=80)
        await fetch_top_shows_cast()

        await update_status(request_id=request_id,
                            step="Completed",
                            progress=100)

    except Exception as e:
        await set_error(request_id=request_id, error=str(e))


async def ingest_all_shows(request_id: str):
    """Fetch all shows from API and insert into SQLite using bulk insert"""
    await init_db()
    shows = await fetch_all_shows(request_id=request_id)
    processed_at = datetime.utcnow().isoformat()

    # Build rows for bulk insert
    rows = [
        (
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
        )
        for show in shows
    ]

    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany("""
            INSERT OR REPLACE INTO All_Shows 
            (id, name, type, language, genres, status, premiered, ended,
             rating_average, summary, updated, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

        await db.commit()


async def compute_top_shows(years: int = 10):
    """Compute top 10 English Action shows from the last N years."""
    await create_top_shows_table()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM Top_Shows")
        processed_at = datetime.utcnow().isoformat()

        # Calculate minimum year in Python to prevent SQL injection
        min_date = datetime.now() - timedelta(days=years * 365)
        min_year = min_date.year

        # Use parameterized query - all user input is passed as parameters
        query = """
        INSERT INTO Top_Shows (id, name, language, genres, premiered, rating_average, processed_at)
        SELECT id, name, language, genres, premiered, rating_average, ?
        FROM All_Shows
        WHERE language='English'
          AND genres LIKE '%Action%'
          AND premiered IS NOT NULL
          AND CAST(substr(premiered, 1, 4) AS INTEGER) >= ?
        ORDER BY rating_average DESC
        LIMIT 10
        """
        await db.execute(query, (processed_at, min_year))
        await db.commit()


async def fetch_top_shows_cast():
    """Fetch cast for each top show and save to Top_Shows_Cast."""
    await create_top_shows_cast_table()
    processed_at = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        # Get top shows from the DB
        top_shows = await db.execute_fetchall("SELECT id, name FROM Top_Shows")
        await db.execute("DELETE FROM Top_Shows_Cast")
        await db.commit()

    # Fetch cast concurrently for all shows
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [fetch_cast(show_id, client) for show_id, _ in top_shows]
        cast_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Insert all cast data
    async with aiosqlite.connect(DB_PATH) as db:
        for (show_id, show_name), cast_data in zip(top_shows, cast_results):
            try:
                if isinstance(cast_data, Exception):
                    log.error(f"Failed fetching cast for show {show_id}: {cast_data}")
                    continue

                for entry in cast_data:
                    person = entry.get("person", {})
                    character = entry.get("character", {})

                    await db.execute("""
                        INSERT INTO Top_Shows_Cast (
                            show_id, show_name, person_id, person_name, 
                            person_birthday, person_deathday, person_gender,
                            person_country_name, character_id, character_name,
                            image, processed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        show_id,
                        show_name,
                        person.get("id"),
                        person.get("name"),
                        person.get("birthday"),
                        person.get("deathday"),
                        person.get("gender"),
                        (person.get("country") or {}).get("name"),
                        character.get("id"),
                        character.get("name"),
                        (character.get("image") or {}).get("original"),
                        processed_at
                    ))
            except Exception as e:
                log.error(f"Failed processing cast for show {show_id}: {e}")

        await db.commit()
