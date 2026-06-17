FROM python:3.14.5-alpine3.23

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /app

RUN apk update && apk upgrade && \
    apk add --no-cache curl bash openjdk21

RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup -s /bin/bash

COPY --chown=appuser:appgroup ./api /app

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt --no-cache-dir

RUN cd /opt && mkdir jars

RUN wget https://jdbc.postgresql.org/download/postgresql-42.7.3.jar \
    -O /opt/jars/postgresql-42.7.3.jar

RUN chown -R appuser:appgroup /opt/jars
RUN chown -R appuser:appgroup /app/models

HEALTHCHECK --interval=30s --timeout=5s CMD curl -o /dev/null -s -w "%{http_code}\n" localhost:5000/healthcheck || exit 1

USER appuser

CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:5000", "server:app"]