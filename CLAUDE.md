# tabManagerServer

## Build / run
- Full stack: `docker compose up --build` (nginx on :89)
- Backend dev: `cd backend && pip install -r requirements.txt greenlet && uvicorn app.main:app --port 8000`
- Frontend dev: `cd frontend && npm install && npm run dev` (proxies `/api` → localhost:8000)
- Frontend build: `cd frontend && npm run build`

## Test
- No test suite. Verify API with curl against `http://localhost:8000/api/...`; verify UI drag-and-drop with Playwright.

## Lessons
- 2026-10-02: `sqlalchemy>=2.0.0` pulls greenlet → it doesn't on python:3.14 (Docker backend crash-looped); requirements now use `sqlalchemy[asyncio]`.
- 2026-10-02: routes live at `/bookmarks/...` → all routers are mounted under `/api` prefix (`app/main.py`).
- 2026-10-02: moving a bookmark across collections → `POST /api/bookmarks/reorder` with `type: "bookmark"` and per-item `collection_id`.
- 2026-10-02: assumed localhost:8000 is this backend → another service owns :8000 on this machine; for tests run backend in a venv on another port with `DATABASE_URL=sqlite+aiosqlite:///<tmp>/test.db`.
- 2026-10-02: HTML5 drag-and-drop covers mobile → touch never starts native drags; touch path lives in `frontend/src/composables/touchDrag.js`. Test it in Playwright with `hasTouch` + CDP `Input.dispatchTouchEvent` (long-press ≥350ms for bookmarks).
