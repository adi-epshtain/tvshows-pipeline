import httpx

BASE_URL = "https://api.tvmaze.com"


async def fetch_all_shows() -> list:
    """Fetch all shows from TV Maze API"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/shows")
        response.raise_for_status()
        return response.json()


async def fetch_cast(show_id: int) -> list:
    """Fetch cast for a specific show by ID asynchronously"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/shows/{show_id}/cast")
        response.raise_for_status()
        return response.json()
