from airflow.sdk import dag, task, Variable
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
from requests import post

import logging


@dag(
    dag_id="data_ingestion_ml_dag",
    start_date=datetime(2026, 6, 5),
    schedule="15 * * * *",              # It runs every hour at the 15th minute
    catchup=False,
    params={
        "sheetName": "Total",
        "fileName": "Datos mismo archivo.xlsx",
        "ml_test_size": 0.2,
        "ml_train_size": 0.8,
        "model_name": "neural_network"
    }
)
def data_ingestion_ml_dag():
    @task(task_id="raw_to_bronze")
    def ingest_data(api_url: str, filename: str, sheet_name: str):
        ENDPOINT = Variable.get("extract_endpoint")
        BODY = { "file_name": filename, "sheet_name": sheet_name }

        logging.info(f"Sending API request to {ENDPOINT} with body: {BODY}")
        logging.info(f"Full API URL: http://{api_url}{ENDPOINT}")
        RES = post(f"http://{api_url}{ENDPOINT}", json=BODY)
        logging.info(f"API response: {RES.text}")
        JSON = RES.json()
        logging.info(f"API response: {JSON}")
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    @task(task_id="bronze_to_silver")
    def clean_data(api_url: str):
        ENDPOINT = Variable.get("clean_endpoint")

        RES = post(f"http://{api_url}{ENDPOINT}")
        JSON = RES.json()

        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    @task(task_id="silver_to_ml_gold")
    def transform_ml_gold_data(api_url: str):
        ENDPOINT = Variable.get("fill_endpoint")

        RES = post(f"http://{api_url}{ENDPOINT}")
        JSON = RES.json()

        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    API_URL = Variable.get("api_url")

    extract_task = ingest_data(API_URL, "{{ params.fileName }}", "{{ params.sheetName }}")
    clean_task = clean_data(API_URL)
    gold_task = transform_ml_gold_data(API_URL)
    train_task = TriggerDagRunOperator(
        task_id="trigger_train_ml_model_dag",
        trigger_dag_id="train_ml_model",
        conf={
            "train_size": "{{ params.ml_train_size }}",
            "test_size": "{{ params.ml_test_size }}",
            "model_name": "{{ params.model_name }}"
        }
    )

    extract_task >> clean_task >> gold_task >> train_task

data_ingestion_ml_dag()