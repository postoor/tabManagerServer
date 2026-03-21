FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite data dir
RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite+aiosqlite:///./data/tabmanager.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
