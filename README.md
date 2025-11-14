# TV Shows Pipeline

## Overview
This project implements a small, production-style
**data pipeline and REST service** built with **FastAPI**.  
It fetches TV shows and their cast from the public
[TVMaze API](https://api.tvmaze.com), processes the data, and exposes
it via Dockerized REST endpoints.

---

## Tech Stack
- **Python 3.11**
- **FastAPI** (async REST framework)
- **SQLite** (lightweight persistent storage)
- **aioSQLite / httpx** for async DB and HTTP
- **Docker & docker-compose**

---

## ⚙️ Setup & Run

### Clone and build
```bash
git clone https://github.com/<your-user>/tvshows-pipeline.git
cd tvshows-pipeline
docker-compose up --build
```

## Test via Swagger
Once the service is running, open the interactive Swagger UI provided by FastAPI:
http://localhost:8000/docs

---
# Database

### View the SQLite Database Online
After the pipeline runs, a local file tvshows.db will be created,  
You can easily inspect its content using an online SQLite viewer:
https://sqliteviewer.app/

### Tables  
All_Shows - all raw shows from TVMaze  
Top_Shows - filtered English Action shows  
Top_Shows_Cast - cast members and characters of top shows  

---

## Design Notes
* Async architecture – all HTTP calls, DB operations, and pipeline steps run fully async (httpx + aiosqlite).
* Modular structure – clear separation between API routers, pipeline orchestration, DB layer, and TVMaze API client.
* Background pipeline execution – long-running ETL flow runs as a FastAPI Background Task, returning 202 Accepted immediately without blocking the client.
* Progress tracking – pipeline exposes a `/pipeline/status` endpoint with live progress, step name, and error state, supporting long-polling and UI progress bars.
* Controlled concurrency – TVMaze fetching uses asyncio.Semaphore to prevent API overload and keep network utilization predictable.
* Resilient HTTP layer – built-in retry with incremental backoff, request timeouts, and structured pagination handling (TVMaze uses HTTP 404 to indicate end-of-data).
* Efficient ingestion – batch (bulk) inserts into SQLite dramatically reduce transaction overhead and improve ETL throughput.
* Dockerized deployment – isolated, predictable environment for running, testing, and shipping the service.

```md
## Sequence Diagram – Pipeline Flow

User
  │
  │ POST /pipeline/update        (202 Accepted)
  ▼
FastAPI (Update Endpoint)
  │
  ├── triggers Background Task → run_full_pipeline()
  │
  ▼
Pipeline Orchestrator
  │
  ├── update_status("Fetching all shows", %)
  ├── ingest_all_shows()
  │       └── fetch_all_shows() → concurrent paginated HTTP calls
  │
  ├── update_status("Computing top shows", %)
  ├── compute_top_shows()
  │
  ├── update_status("Fetching cast", %)
  ├── fetch_top_shows_cast()
  │
  └── update_status("Completed", 100)

Meanwhile…

User
  │
  │ GET /pipeline/status         (polling)
  ▼
FastAPI (Status Endpoint)
  │
  └── returns current progress, step, running flag, and errors.
  ```

---
## Author
**Adi Epshtain**  
Senior Python Backend Developer
[LinkedIn](https://www.linkedin.com/in/adi-epshtain-backend/)