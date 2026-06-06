FROM python:3.14.5-alpine3.23

WORKDIR /app

RUN addgroup -s appuser appgroup && \
    adduser -G appgroup appuser

COPY --chown=appuser:appgroup ./api /app

RUN apk update && apk upgrade && \
    apk add --no-cache curl bash openjdk21

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk/bin
ENV PATH=$JAVA_HOME/bin:$PATH

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt --no-cache-dir

RUN chown -R appuser:appgroup /app

HEALTHCHECK --interval=30s --timeout=5s CMD curl -o /dev/null -s -w "%{http_code}\n" localhost:5000/healthcheck || exit 1

USER appuser

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]