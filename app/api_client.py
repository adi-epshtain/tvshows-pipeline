import asyncio
from dataclasses import dataclass
from typing import List

import httpx

from app.logger import log
from app.pipeline_status import update_status

BASE_URL = "https://api.tvmaze.com"
MAX_CONCURRENT_REQUESTS = 10  # tune up/down depending on your network
CONCURRENCY_LIMIT = 5
MAX_RETRIES = 3
BACKOFF_BASE = 0.5  # seconds
TOTAL_PAGES_ESTIMATE = 260
FETCH_SHOWS_WEIGHT = 70   # from 100% from pipline


@dataclass
class PageResult:
    data: List[dict]
    is_last_page: bool


async def fetch_page(client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore) -> PageResult:
    """Fetch a single page with concurrency control + retry logic"""
    async with sem:

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response: httpx.Response = await client.get(f"{BASE_URL}/shows?page={page}")

                # TVmaze signals end-of-data using 404
                if response.status_code == 404:
                    return PageResult(data=[], is_last_page=True)

                response.raise_for_status()
                return PageResult(data=response.json(), is_last_page=False)

            except Exception as e:
                log.warning(
                    f"[Page {page}] Attempt {attempt}/{MAX_RETRIES} failed: {e}"
                )

                # if last attempt failed → stop retrying
                if attempt == MAX_RETRIES:
                    return PageResult(data=[], is_last_page=False)

                # backoff before retrying
                await asyncio.sleep(BACKOFF_BASE * attempt)


async def fetch_all_shows(request_id: str) -> list:
    """Fetch all shows from TVMaze with structured pagination + progress updates"""
    all_shows = []
    page = 0
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with httpx.AsyncClient(timeout=20) as client:
        while True:

            # build batch of concurrent fetches
            tasks = [
                fetch_page(client, p, sem)
                for p in range(page, page + CONCURRENCY_LIMIT)
            ]
            results: tuple[PageResult, ...] = await asyncio.gather(*tasks)

            # append all page data
            for result in results:
                all_shows.extend(result.data)

            # PROGRESS UPDATE - calculate weighted progress
            pages_fetched = page + CONCURRENCY_LIMIT
            ratio = min(pages_fetched / TOTAL_PAGES_ESTIMATE, 1.0)
            weighted_progress = int(ratio * FETCH_SHOWS_WEIGHT)

            await update_status(request_id=request_id,
                                step=f"Fetching all shows (page {page})",
                                progress=weighted_progress)

            # stop if ANY page in the batch is the last
            if any(result.is_last_page for result in results):
                break

            log.info(
                f"Fetched pages {page}-{page + CONCURRENCY_LIMIT - 1} "
                f"→ total shows: {len(all_shows)}"
            )

            page += CONCURRENCY_LIMIT
            await asyncio.sleep(0.5)

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
