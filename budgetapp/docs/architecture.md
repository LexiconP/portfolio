# Free Receipt OCR Budget Reconciliation App — Architecture Design

## Goals
- 100% free to use for end users.
- 100% free to operate (no paid services).
- Accept receipt images, extract data via OCR, reconcile against a personal budget.
- Export results as CSV for low‑tech everyday users.
- Privacy-first: data stored locally or in a self-hosted setup.

## Non-Goals
- Real‑time bank integrations.
- Paid OCR services.
- Heavy ML training pipelines.

## Proposed Free Stack
**Client**
- Simple HTML/CSS/JS UI served by the backend
- CSV export via backend endpoint
- Optional offline-first storage: IndexedDB (future)

**Backend (Self‑Hosted, Free)**
- API: FastAPI (Python)
- OCR: Tesseract OCR (open source)
- Data store: SQLite (single-user)
- Object storage: local filesystem (images)
- Modular OOP layers: API → services → repositories → database

**Deployment**
- Local machine, Raspberry Pi, or free tier VM (if available)
- Docker Compose for portability

## High-Level Architecture
```
[User Device]
    |  (Upload receipt image)
    v
[Web App / PWA]
    |  (POST /receipts)
    v
[FastAPI Backend]
    |  -> Save image to /data/receipts
    |  -> OCR via Tesseract
    |  -> Parse fields (date, vendor, items, total)
    |  -> Store in DB (Receipts, Budgets)
    v
[Budget Reconciliation]
    |  -> Match receipt items to budget categories
    |  -> Update budget balances
    v
[CSV Export]
    |  -> Generate CSV (client or server)
```

## Components
### 1) Web App (PWA)
- Upload receipts
- Review OCR results
- Edit categories
- Export CSV
- Offline capture with later sync (optional)

### 2) API Service (FastAPI)
- Endpoints:
  - `POST /receipts` — upload and OCR
  - `GET /receipts` — list receipts
  - `GET /budgets` — list budgets
  - `POST /budgets` — update budgets
  - `GET /export` — CSV export (optional)

### 2.1) API Modules
- `app/api/routes.py` — route handlers and request models
- `app/core/container.py` — dependency wiring

### 3) OCR Module (Tesseract)
- Preprocessing with OpenCV (optional)
- Confidence scores per field

### 4) Budget Reconciliation
- Rules-based mapping (vendor → category)
- Manual override UI

### 5) Data Storage
- SQLite (default)
- Schema:
    - `receipts(id, date, vendor, total, image_path, ocr_text, created_at)`
  - `budgets(id, category, monthly_limit, spent)`

## Code Structure (OOP)
- `app/core` — config, database, interfaces, container
- `app/services` — receipt/budget business logic
- `app/repositories` — SQL access
- `app/api` — FastAPI routes and models
- `app/static` — HTML/CSS/JS UI

## Data Flow
1. User uploads receipt image.
2. Backend stores file and runs OCR.
3. Parsed text → receipt fields.
4. User reviews and corrects.
5. System reconciles against budget.
6. CSV exported for user records.

## Security & Privacy
- Local/self-hosted by default.
- No third-party data sharing.
- Optional encryption at rest (filesystem encryption).

## Operations & Cost
- Free OCR (Tesseract)
- Free frameworks and libraries
- Compute on local device or free-tier VM

## Tests
- Pytest-based unit tests for receipt flow.
- Focus on storage, OCR integration, parsing, and repository inserts.

## MVP Scope
- Upload receipt
- OCR to text
- Manual correction
- Budget category mapping
- CSV export

## Future Enhancements
- Multi-user auth
- Smart categorization with local ML
- Receipt template detection
- Scheduled CSV export
