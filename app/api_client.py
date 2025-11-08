import httpx

SHOWS_URL = "https://api.tvmaze.com/shows"


async def fetch_all_shows() -> list:
    """Fetch all shows from TV Maze API"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(SHOWS_URL)
        response.raise_for_status()
        return response.json()
