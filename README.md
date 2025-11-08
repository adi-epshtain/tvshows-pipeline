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
* Async architecture - all HTTP and DB operations are async (httpx + aiosqlite)
* Modular structure - clear separation between API, DB, and pipeline logic
* Dockerized deployment - easy to run and test 
* Error handling - basic error handling for HTTP and DB operations


---
## Author
**Adi Epshtain**  
Senior Python Backend Developer
[LinkedIn](https://www.linkedin.com/in/adi-epshtain-backend/)