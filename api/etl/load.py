from pyspark.sql import DataFrame


def load_to_db(
    df: DataFrame,
    table_name: str,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    schema: str = "public",
):
    """
    Loads a DataFrame into a PostgreSQL database table. Creates the schema if it does not exist.

    Args:
        df (DataFrame): The DataFrame to load into the database.
        table_name (str): The name of the target table in the database.
        user (str): The database user.
        password (str): The database password.
        host (str): The database host.
        port (str): The database port.
        database (str): The database name.
        schema (str, optional): The schema to use. Defaults to "public".
    """
    URL = f"jdbc:postgresql://{host}:{port}/{database}"

    df.write.jdbc(
        URL,
        table=f"{schema}.{table_name}",
        mode="overwrite",
        properties={
            "user": user,
            "password": password,
            "driver": "org.postgresql.Driver",
        },
    )
