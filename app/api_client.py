import asyncio

import httpx

from app.logger import log

BASE_URL = "https://api.tvmaze.com"


async def fetch_all_shows(retries: int = 3, backoff: float = 1.5) -> list:
    """Fetch all shows from TVMaze API with retries and error handling"""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(f"{BASE_URL}/shows")
                resp.raise_for_status()
                log.info(f"Successfully fetched all shows (attempt {attempt})")
                return resp.json()
        except httpx.TimeoutException:
            log.warning(f"Timeout fetching shows (attempt {attempt}/{retries})")
        except httpx.RequestError as e:
            log.warning(f"Network error fetching shows: {e}")
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP error {e.response.status_code} while fetching shows")
            break

        await asyncio.sleep(backoff * attempt)  # exponential backoff

    log.error("Failed to fetch shows after multiple attempts.")
    return []


async def fetch_cast(show_id: int, retries: int = 3, backoff: float = 1.5) -> list:
    """Fetch cast for a specific show by ID"""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{BASE_URL}/shows/{show_id}/cast")
                resp.raise_for_status()
                log.info(f"Cast fetched for show {show_id} (attempt {attempt})")
                return resp.json()
        except httpx.TimeoutException:
            log.warning(f"Timeout fetching cast for show {show_id} (attempt {attempt})")
        except httpx.RequestError as e:
            log.warning(f"Network error fetching cast for show {show_id}: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                log.info(f"Show {show_id} not found (404). Skipping.")
                return []
            log.error(f"HTTP {e.response.status_code} for show {show_id}")
            break

        await asyncio.sleep(backoff * attempt)

    log.error(f"Failed to fetch cast for show {show_id} after multiple attempts.")
    return []
