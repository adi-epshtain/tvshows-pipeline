import aiosqlite

from app.logger import log

DB_PATH = "tvshows.db"


async def init_db():
    """Initialize SQLite tables if not exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS All_Shows (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            language TEXT,
            genres TEXT,
            status TEXT,
            premiered TEXT,
            ended TEXT,
            rating_average REAL,
            summary TEXT,
            updated INTEGER,
            processed_at TEXT
        )""")
        await db.commit()
    log.info("All_Shows table initialized")


async def create_top_shows_table():
    """Create Top_Shows table if not exists."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS Top_Shows (
            id INTEGER PRIMARY KEY,
            name TEXT,
            language TEXT,
            genres TEXT,
            premiered TEXT,
            rating_average REAL,
            processed_at TEXT
        )""")
        await db.commit()
    log.info("Top_Shows table initialized")


async def create_top_shows_cast_table():
    """Create Top_Shows_Cast table if not exists."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS Top_Shows_Cast (
            show_id INTEGER,
            show_name TEXT,
            person_id INTEGER,
            person_name TEXT,
            person_birthday TEXT,
            person_deathday TEXT,
            person_gender TEXT,
            person_country_name TEXT,
            character_id INTEGER,
            character_name TEXT,
            image TEXT,
            processed_at TEXT
        )
        """)
        await db.commit()
    log.info("Top_Shows_Cast table initialized")
