FROM python:3.14.5-slim

WORKDIR /app

RUN groupadd appgroup && \
    useradd -G appgroup appuser

COPY --chown=appuser:appgroup ./api /app

RUN apt update && \
    apt install curl -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt --no-cache-dir

RUN chown -R appuser:appgroup /app

HEALTHCHECK --interval=30s --timeout=5s CMD curl -o /dev/null -s -w "%{http_code}\n" localhost:5000/healthcheck || exit 1

USER appuser

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]