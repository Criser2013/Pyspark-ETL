ARG AIRFLOW_VERSION=slim-3.2.2-python3.13

FROM apache/airflow:${AIRFLOW_VERSION}

USER root

COPY ./entrypoint.sh /entrypoint.sh
COPY ./requirements.txt /requirements.txt
RUN chmod +x /entrypoint.sh
RUN apt update && apt upgrade -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt

ENTRYPOINT ["/entrypoint.sh"]