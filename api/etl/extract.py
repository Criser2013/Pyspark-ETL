from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
from pandas import read_excel


def extract_excel(
    spark_session: SparkSession, path: str, schema: StructType | None = None, sheet_name: str | int = 0
) -> DataFrame:
    """
    Reads an Excel file and returns a DataFrame. Treats common placeholders as NA.

    Args:
        spark_session (SparkSession): The PySpark session.
        path (str): The file path to the Excel file.
        schema (StructType | None, optional): The schema for the DataFrame. Defaults to None.
        sheet_name (str|int, optional): The sheet name or index to read. Defaults to 0 (first sheet).

    Returns:
        DataFrame: A PySpark DataFrame containing the data from the specified Excel sheet.
    """
    NA = ["NA", "NaN", "", "na", "N/A", "en estudio"]
    DF = read_excel(path, sheet_name=sheet_name, na_values=NA)
    return spark_session.createDataFrame(DF, schema=schema)


def extract_sql(
    spark_session: SparkSession,
    table: str,
    user: str,
    password: str,
    host: str,
    port: str,
    database: str,
    dtypes: dict | None = None,
) -> DataFrame:
    """
    Extracts data from a PostgreSQL database and returns a DataFrame.

    Args:
        spark_session (SparkSession): The PySpark session.
        table (str): The table name to extract data from.
        user (str): The database user.
        password (str): The database password.
        host (str): The database host.
        port (str): The database port.
        database (str): The database name.
    Returns:
        DataFrame: A PySpark DataFrame containing the results of the SQL query.
    """
    URL = f"jdbc:postgresql://{host}:{port}/{database}"
    return spark_session.read.jdbc(
        URL,
        table,
        properties={
            "user": user,
            "password": password,
            "driver": "org.postgresql.Driver",
        },
    )