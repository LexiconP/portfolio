# portfolio
Public portfolio

## App Overview
This repository contains a free, self‑hosted receipt OCR budgeting app. It accepts receipt images, extracts text with Tesseract OCR, parses key fields, and stores results in SQLite. Budgets can be managed and exported as CSV.

## Architecture
See [architecture.md](architecture.md).

## Docker
Build and run the API:
- `docker compose up --build`

Health check:
- `http://localhost:8000/health`

Web UI:
- `http://localhost:8000/`

## Project Structure
- `backend/app/api` — FastAPI routes and request models
- `backend/app/core` — config, database, DI container, interfaces
- `backend/app/repositories` — SQL repositories
- `backend/app/services` — receipt/budget business logic
- `backend/app/static` — HTML/CSS/JS UI
- `backend/tests` — pytest tests
- `docs` — architecture and documentation

## Tests
From the `budgetapp` folder:
- `pip install -r backend/requirements-dev.txt`
- `pytest backend/tests`

## API Endpoints
- `GET /health`
- `POST /receipts`
- `GET /receipts`
- `GET /receipts/{id}`
- `GET /export`
- `GET /budgets`
- `POST /budgets`
