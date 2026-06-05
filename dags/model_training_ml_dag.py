from airflow.sdk import dag, task, Variable
#from airflow.providers.standard.sensors.external_task import ExternalTaskSensor
from datetime import datetime#, timedelta
from requests import post

import logging

@dag(
    dag_id="train_ml_model",
    start_date=datetime(2026, 6, 5),
    catchup=False,
    params={
        "train_size": 0.2,
        "test_size": 0.8,
        "model_name": "neural_network"
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

    @task(task_id="model_export")
    def export_ml_model(api_url: str, model_name: str):
        ENDPOINT = Variable.get("model_export_endpoint")
        BODY = { "model_name": model_name }

        RES = post(f"http://{api_url}{ENDPOINT}", json=BODY)
        JSON = RES.json()
        
        if JSON["success"]:
            logging.info(JSON["message"])
        else:
            raise Exception(f"API request failed: {JSON['message']}")
    """
    sensor_task = ExternalTaskSensor(
        task_id="wait_for_training_data",
        external_dag_id="data_ingestion_ml_dag",
        external_task_id="silver_to_ml_gold",
        execution_delta=timedelta(minutes=5)            # Looks for an execution of independent DAG 5 minutes before execution time of this DAG
    )                                                   # On standard configuration, it will await to find an execution of the independent DAG that has the same execution timestamp as this DAG. With execution_delta, it will look for an execution with a shifted execution date.
    """
    API_URL = Variable.get("api_url")
    instantiate_task = instantiate_pipeline(API_URL)
    split_task = split_train_test(API_URL, "{{ params.train_size }}", "{{ params.test_size }}")
    train_task = train_ml_model(API_URL)
    evaluate_task = evaluate_ml_model(API_URL)
    export_task = export_ml_model(API_URL, "{{ params.model_name }}")

    [instantiate_task, split_task] >> train_task >> [evaluate_task, export_task]

    #sensor_task >> 

train_ml_model_dag()