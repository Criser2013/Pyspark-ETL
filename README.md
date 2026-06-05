# ETL for Pulmonary Embolism prediction

This is an improved variant of ETL process seen at [Pulmonary Embolism prediction project](https://github.com/Criser2013/Diagnostico-TEP/blob/main/preprocesamiento/Datos%20entrenamiento.ipynb), still using **Pandas** but combining it with **Apache Airflow** to orchestrate data ingestion, processing and ML models building automatically.


## Tech stack

- **`pandas`:** To run ETL script following *Medallion architecture*.
- **`scikit-learn`:** To standarize data used to train ML models.
- **`airflow`:** Was used to orchestrate the entire pipeline.
- **`flask`:** To develop a small backend server with the purpose of allowing access to **Pandas** and **Scikit** features to Airflow container without needing to increase Airflow image weight and complexity adding more packages and maintaining their responsabilities separed.
- **`postgres`:** Selected data warehouse engine.
- **`docker compose`:** To easily run each service and allow interactions among between them.

Lightweight images of **Postgres**, **Python** and **Airflow** were used to achieve maximum performance with abscence of unnecessary dependencies.

## How to run?

1. Create a `.env` file following template available on `.env.example` file.
2. Open a shell and start containers and images building.
```bash
docker compose up --build -d
```

3. After the containers started and everyone show a `healthy` status, open your web browser an go to `http://localhost:8080`.
4. Sign in on `Airflow UI` using the credentials declared at `.env` file.
5. Once logged, go to **DAGS** section and trigger the DAG called `data_ingestion_ml`.
6. Fill in the parameters acording to your preferences and run it!
7. When the DAG finished, it will trigger `model_training_ml` DAG automatically to train, assess and export ML model.

Once DAG finished, ML data will be available at `gold` schema on `ml_train_pe_data` table.

## Utilitary commands

- **Destroy containers and volume deletion**:
```bash
docker compose down -v
```

- **Execute a command on a container:**
```bash
docker compose exec <container-name> <command>
```

- **Check database schemas:**
```psql
\dn
```

- **See database tables:**
```psql
\dt <schema>.*
```

- **Watch table structure:**
```psql
\d <schema>.<table>
```

- **Log into Postgres instance:**
```bash
psql -W --username <DB_USERNAME> --dbname <DB_NAME>
```

## Outcome
ML model trained exported on ONNX ready to be deployed on web applications, also dataset ready for ML training and data analytics. Raw pipeline can be found on `/api/models` exported as **Pickle** serializable objects.
