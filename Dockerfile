# --- Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Final Stage ---
FROM python:3.11-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
# Set path for virtual environment and explicitly inject /app into Python path
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Create volatile directories required by upload pipelines
RUN mkdir -p /tmp/uploads && chmod 777 /tmp/uploads

# Transfer app source files
COPY ./app ./app

EXPOSE 8000

# Tell Uvicorn to look inside the app module package for the application instance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]