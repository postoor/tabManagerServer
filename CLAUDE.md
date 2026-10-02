# tabManagerServer

## Build / run
- Full stack: `docker compose up --build` (nginx on :89)
- Backend dev: `cd backend && pip install -r requirements.txt greenlet && uvicorn app.main:app --port 8000`
- Frontend dev: `cd frontend && npm install && npm run dev` (proxies `/api` → localhost:8000)
- Frontend build: `cd frontend && npm run build`

## Test
- No test suite. Verify API with curl against `http://localhost:8000/api/...`; verify UI drag-and-drop with Playwright.

## Lessons
- 2026-10-02: requirements.txt is enough for async SQLAlchemy → local venv also needs `greenlet` or uvicorn fails at import.
- 2026-10-02: routes live at `/bookmarks/...` → all routers are mounted under `/api` prefix (`app/main.py`).
- 2026-10-02: moving a bookmark across collections → `POST /api/bookmarks/reorder` with `type: "bookmark"` and per-item `collection_id`.
