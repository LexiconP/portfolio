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
- Web app (PWA) for mobile & desktop
- Framework: React + Vite (open source)
- CSV export: client-side generation
- Optional offline-first storage: IndexedDB

**Backend (Self‑Hosted, Free)**
- API: FastAPI (Python)
- OCR: Tesseract OCR (open source)
- Data store: SQLite (single-user) or Postgres (multi-user)
- Object storage: local filesystem (images)
- Background jobs: built‑in FastAPI background tasks or Celery + Redis (optional)

**Deployment**
- Local machine, Raspberry Pi, or free tier VM (if available)
- Docker optional for portability

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
    |  -> Store in DB (Receipts, Items)
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

### 3) OCR Module (Tesseract)
- Preprocessing with OpenCV (optional)
- Confidence scores per field

### 4) Budget Reconciliation
- Rules-based mapping (vendor → category)
- Manual override UI

### 5) Data Storage
- SQLite (default)
- Schema:
  - `receipts(id, date, vendor, total, image_path)`
  - `items(id, receipt_id, name, price, category)`
  - `budgets(id, category, monthly_limit, spent)`

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
