from etl.extract import extract_excel, extract_sql
from etl.load import load_to_db
from etl.transform import transform_to_clean_data, transform_ml_data
from ml.data import split_data
from ml.model import create_model, train_model, evaluate_model
from ml.io import save_pipeline, load_untrained_pipeline, load_trained_pipeline
from constants import DTYPES, NUMS, BOOLEANS
from pandas import DataFrame
from pyspark.sql import SparkSession
from utils import remove_accents
from re import sub
from sqlalchemy import create_engine

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
from shutil import rmtree

load_dotenv()

DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_NAME = getenv("DB_NAME")

app = Flask(__name__)
app.spark = (
    SparkSession.builder.appName("PE_Prediction")
    .config("spark.jars", "/opt/jars/postgresql-42.7.3.jar")
    .getOrCreate()
)


@app.route("/raw-to-bronze", methods=["POST"])
def extract_data():
    try:
        request_data = request.get_json()
        PATH = f"/app/data/{request_data['file_name']}"
        AUX = BOOLEANS.copy()
        AUX[2] = "Procedimiento Quirurgicos / Traumatismo Grave en los últimos 15 dias"
        COLS = NUMS + AUX + ["Edad", "Género", "Otra Enfermedad", "Fiebre", "TEP"]

        AUX_CLEAN = map(lambda x: remove_accents(sub(r"-|/| ", "_", x)), COLS)
        MAPPER = dict(zip(COLS, AUX_CLEAN))
        MAPPER[
            "Procedimiento Quirurgicos / Traumatismo Grave en los últimos 15 dias"
        ] = "Cirugia_reciente"

        df = extract_excel(app.spark, PATH, request_data["sheet_name"], DTYPES, COLS)
        df = df.withColumnsRenamed(MAPPER)

        load_to_db(
            df, "raw_pe_data", DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, "bronze"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Raw data extracted and loaded successfully. {df.count()} rows processed.",
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/bronze-to-silver", methods=["POST"])
def transform_data():
    try:
        df = extract_sql(
            app.spark,
            "bronze.raw_pe_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
        df = transform_to_clean_data(df)

        load_to_db(
            df,
            "clean_pe_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
            "silver",
        )
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Data cleaned and filled successfully. {df.count()} rows processed.",
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/silver-to-gold", methods=["POST"])
def load_data():
    try:
        df = extract_sql(
            app.spark,
            "silver.clean_pe_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
        df = transform_ml_data(df)
        load_to_db(
            df,
            "ml_train_pe_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
            "gold",
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"ML training data prepared successfully. {df.count()} rows processed.",
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/instantiate-ml-pipeline", methods=["POST"])
def instantiate_ml_pipeline():
    try:
        PATH = "/app/models/untrained_pipeline"

        if Path(PATH).exists():
            rmtree(PATH)

        pipeline = create_model()
        save_pipeline(pipeline, PATH)
        return (
            jsonify(
                {"success": True, "message": "ML pipeline instantiated successfully."}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/split-ml-data", methods=["POST"])
def split_ml_data():
    try:
        request_data = request.get_json()
        df = extract_sql(
            app.spark,
            "gold.ml_train_pe_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
        train, test = split_data(
            df, request_data["train_size"], request_data["test_size"]
        )

        load_to_db(
            train,
            "train_ml_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
            "gold",
        )
        load_to_db(
            test,
            "test_ml_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
            "gold",
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"ML data split successfully. Train: {train.count()} rows, Test: {test.count()} rows",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/train-ml-model", methods=["POST"])
def train_ml_model():
    try:
        path = "/app/models/untrained_pipeline"
        pipeline = load_untrained_pipeline(path)

        train_data = extract_sql(
            app.spark,
            "gold.train_ml_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
        pipeline = train_model(pipeline, train_data)

        path = path.replace("untrained", "trained")
        save_pipeline(pipeline, path)

        return (
            jsonify(
                {"success": True, "message": "ML model trained and saved successfully."}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/evaluate-ml-model", methods=["POST"])
def evaluate_ml_model():
    try:
        PATH = "/app/models/trained_pipeline"
        pipeline = load_trained_pipeline(PATH)

        test_data = extract_sql(
            app.spark,
            "gold.test_ml_data",
            DB_USER,
            DB_PASSWORD,
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
        metrics = evaluate_model(pipeline, test_data)

        # Save metrics to PostgreSQL using SQLAlchemy
        ENGINE = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        df_metrics = DataFrame(metrics, index=[0])
        df_metrics.to_sql("model_metrics", con=ENGINE, if_exists="replace", index=False)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "ML model evaluated successfully.",
                    "metrics": metrics,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"success": True, "message": "healthy"}), 200


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)
