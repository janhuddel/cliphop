FROM python:3.12-slim

ARG VERSION=1.0.3
LABEL org.opencontainers.image.title="cliphop" \
      org.opencontainers.image.version="${VERSION}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CLIPHOP_DB=/data/cliphop.db

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir . && mkdir -p /data

EXPOSE 8000

# Bewusst ein einziger Worker: Live-Updates laufen über Pub/Sub im Prozess.
CMD ["uvicorn", "cliphop.app:create_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
