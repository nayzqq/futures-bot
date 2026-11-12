FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --uid 1001 botuser \
    && mkdir -p /app/data \
    && chown -R botuser:botuser /app
USER botuser

HEALTHCHECK --interval=60s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, sqlite3; sqlite3.connect(os.getenv('DB_PATH', '/app/data/futures_bot.db')).execute('SELECT 1')" || exit 1

CMD ["python", "main.py"]
