import aiosqlite

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


