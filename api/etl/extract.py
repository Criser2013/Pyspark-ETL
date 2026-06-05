from pandas import read_excel, read_sql, DataFrame
from sqlalchemy import create_engine

def extract_excel(path: str, sheet_name: str|int = 0) -> DataFrame:
    """
    Reads an Excel file and returns a DataFrame. Treats common placeholders as NA.

    Args:
        path (str): The file path to the Excel file.
        sheet_name (str|int, optional): The sheet name or index to read. Defaults to 0 (first sheet).

    Returns:
        DataFrame: A pandas DataFrame containing the data from the specified Excel sheet.
    """
    NA = ["NA", "NaN", "", "na", "N/A", "en estudio"]
    return read_excel(path, sheet_name=sheet_name, na_values=NA)

def extract_sql(query: str, user: str, password: str, host: str, port: str, database: str, dtypes: dict|None = None) -> DataFrame:
    """
    Extracts data from a PostgreSQL database and returns a DataFrame.

    Args:
        query (str): The SQL query to execute.
        user (str): The database user.
        password (str): The database password.
        host (str): The database host.
        port (str): The database port.
        database (str): The database name.
        dtypes (dict|None, optional): A dictionary specifying the data types for the columns. Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame containing the results of the SQL query.
    """
    ENGINE = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    return read_sql(query, ENGINE, dtype=dtypes)