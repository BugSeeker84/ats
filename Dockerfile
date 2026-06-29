# Official Playwright image: Chromium + all required system libraries preinstalled.
# Pinned to the playwright pip version (1.60.0) so the bundled browser matches the API.
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY pyproject.toml ./
COPY ats ./ats
RUN pip install --no-cache-dir . \
    && python -m playwright install chromium

# App code (frontend is served by the backend from ./frontend; profiles/templates/shared
# are read at runtime).
COPY backend ./backend
COPY frontend ./frontend
COPY profiles ./profiles
COPY templates ./templates
COPY shared ./shared

# Render injects $PORT; bind to it (fallback 8000 for local `docker run`).
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
