import asyncio

import httpx

from app.logger import log

BASE_URL = "https://api.tvmaze.com"
MAX_CONCURRENT_REQUESTS = 10  # tune up/down depending on your network
CONCURRENCY_LIMIT = 5  # מגביל ל-5 בקשות במקביל



async def fetch_page(client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore) -> list:
    """Fetch a single page of shows with concurrency control."""
    async with sem:
        try:
            resp = await client.get(f"{BASE_URL}/shows?page={page}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.warning(f"Failed to fetch page {page}: {e}")
            return []


async def fetch_all_shows(max_pages: int | None = None) -> list:
    """Fetch all shows from TVMaze safely with controlled concurrency."""
    all_shows = []
    page = 0
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            if max_pages and page >= max_pages:
                log.info(f"Stopping early after {page} pages (testing mode).")
                break
            tasks = [fetch_page(client, p, sem) for p in range(page, page + CONCURRENCY_LIMIT)]
            results = await asyncio.gather(*tasks)

            if any(r is None for r in results):
                valid = [r for r in results if r]
                for data in valid:
                    all_shows.extend(data)
                break

            for data in results:
                all_shows.extend(data)

            log.info(f"Fetched pages {page}-{page + CONCURRENCY_LIMIT - 1} "
                     f"→ total shows: {len(all_shows)}")
            page += CONCURRENCY_LIMIT
            await asyncio.sleep(0.5)  # tiny delay to avoid rate limiting

    log.info(f"Total shows fetched: {len(all_shows)}")
    return all_shows


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
