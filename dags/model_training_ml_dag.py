from airflow.sdk import dag, task, Variable
from datetime import datetime
from requests import post

import logging

@dag(
    dag_id="train_ml_model",
    start_date=datetime(2026, 6, 5),
    catchup=False,
    params={
        "train_size": 0.2,
        "test_size": 0.8
    }
)
def train_ml_model_dag():
    @task(task_id="instantiate_pipeline")
    def instantiate_pipeline(api_url: str):
        ENDPOINT = Variable.get("pipeline_instantiation_endpoint")

        RES = post(f"http://{api_url}{ENDPOINT}")
        JSON = RES.json()
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    @task(task_id="split_data")
    def split_train_test(api_url: str, train_size: float, test_size: float):
        ENDPOINT = Variable.get("split_data_endpoint")
        BODY = { "train_size": float(train_size), "test_size": float(test_size) }
        logging.info(f"Sending API request to {ENDPOINT} with body: {BODY}")
        RES = post(f"http://{api_url}{ENDPOINT}", json=BODY)
        JSON = RES.json()
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    @task(task_id="train_model", trigger_rule="all_done")
    def train_ml_model(api_url: str):
        ENDPOINT = Variable.get("train_model_endpoint")

        RES = post(f"http://{api_url}{ENDPOINT}")
        JSON = RES.json()
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")
    
    @task(task_id="model_evaluation")
    def evaluate_ml_model(api_url: str):
        ENDPOINT = Variable.get("evaluate_model_endpoint")

        RES = post(f"http://{api_url}{ENDPOINT}")
        JSON = RES.json()
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")

    API_URL = Variable.get("api_url")
    instantiate_task = instantiate_pipeline(API_URL)
    split_task = split_train_test(API_URL, "{{ params.train_size }}", "{{ params.test_size }}")
    train_task = train_ml_model(API_URL)
    evaluate_task = evaluate_ml_model(API_URL)

    [instantiate_task, split_task] >> train_task >> evaluate_task

train_ml_model_dag()