from utils import eval_interval
from constants import NUMS_CLEANED, BOOLEANS_CLEANED, DISEASES_CLEANED
from pyspark.sql import DataFrame, Column
from pyspark.sql.functions import (
    regexp_replace,
    lower,
    when,
    greatest,
    trim,
    col,
    lit,
)


def fill_na_numeric(df: DataFrame) -> DataFrame:
    """
    Fills NA values in numeric columns with the median value of each column and regexp_replaces outliers with the same median value.

    Args:
        df (DataFrame): DataFrame containing the column to be imputed.

    Returns:
        DataFrame: A DataFrame with NA values filled and outliers regexp_replaced.
    """

    for i in NUMS_CLEANED:
        median = df.selectExpr(f"percentile_approx({i}, 0.5) as median").first()[
            "median"
        ]
        Q1 = df.selectExpr(f"percentile_approx({i}, 0.25) as Q1").first()["Q1"]
        Q3 = df.selectExpr(f"percentile_approx({i}, 0.75) as Q3").first()["Q3"]
        RIC = Q3 - Q1

        LOWER_BOUND = Q1 - 1.5 * RIC
        UPPER_BOUND = Q3 + 1.5 * RIC

        df = df.withColumn(
            i, when(col(i).isNull() | col(i).isNaN(), median).otherwise(col(i))
        )
        df = df.withColumn(
            i,
            when((col(i) < LOWER_BOUND) | (col(i) > UPPER_BOUND), median).otherwise(
                col(i)
            ),
        )

    return df


def fill_na_boolean(df: DataFrame) -> DataFrame:
    """
    Fills NA values in boolean columns with the mode value of each column.

    Args:
        df (DataFrame): DataFrame containing the column to be imputed.

    Returns:
        DataFrame: A DataFrame with NA values filled.
    """
    for i in BOOLEANS_CLEANED:
        MODE = df.selectExpr(f"mode({i}) as mode").first()["mode"]
        df = df.withColumn(
            i, when(col(i).isNull() | col(i).isNaN(), lit(MODE)).otherwise(col(i))
        )
    return df


def transform_gender(gender: Column) -> Column:
    """
    Transforms the "Género" column from categorical values ("F", "M") to numeric values (0, 1).

    Args:
        gender (Column): A Column containing the "Género" column with categorical values.

    Returns:
        Column: A Column with the "Género" column transformed to numeric values.
    """
    gender_lower = lower(trim(gender))
    male = regexp_replace(gender_lower, "m", "1")
    female = regexp_replace(male, "f", "0")
    return female.cast("int")


def transform_fever(fever: Column) -> Column:
    """
    Transforms the "Fiebre" column from raw values (temperature in Celsius upper or equal to 38 or binary indicator)
    to a binary indicator (0, 1) where 1 indicates the presence of fever.

    Args:
        fever (Column): A Column representing the "Fiebre" column with raw values.

    Returns:
        Column: A Column with the "Fiebre" column transformed to a binary indicator.
    """
    return when((fever >= 38) | (fever == 1), 1).otherwise(0)


def scale_column(
    column: Column, factor: float, upper_bound: float | None = None
) -> Column:
    """
    Scales the values in a column by a given factor, with an optional upper bound.

    Args:
        column (Column): A Column containing the column to be scaled.
        factor (float): The factor by which to scale the values.
        upper_bound (float|None): The upper bound for the scaled values. If None, uses the factor as the upper bound.

    Returns:
        Column: A Column with the scaled values.
    """
    if upper_bound is None:
        upper_bound = factor

    return when((column > 0) & (column < upper_bound), column * factor).otherwise(
        column
    )


def transform_boolean(data: Column) -> Column:
    """
    Transforms a string representing a boolean value into an integer (1 or 0). Treats common placeholders as NA.

    Args:
        data (Column): The column to transform.

    Returns:
        Column: 1 for true values, 0 for false values.
    """
    data = lower(trim(data))

    data = data.transform(
        lambda x: when(x.isin("1", "0"), x)
        .when(x.isin("ni", "no", "n"), "0")
        .otherwise("1")
    )
    return data.cast("int")


def transform_to_clean_data(df: DataFrame) -> DataFrame:
    """
    Transforms the raw data into a clean format, it involves filling null values, converting
    qualitative variables to quantitative ones and replacing dirty values with clean ones.

    Args:
        df (DataFrame): The raw DataFrame to be transformed.

    Returns:
        DataFrame: A cleaned and transformed DataFrame ready for analysis or modeling.
    """
    df = df.withColumns(
        {
            "Fiebre": transform_fever(col("Fiebre")),
            "HB": regexp_replace("HB", ",", ".").cast("float"),
            "PLT": regexp_replace(regexp_replace("PLT", ",", "."), "OO", "00").cast(
                "float"
            ),
            "Hemoptisis": regexp_replace("Hemoptisis", "N0", "0").cast("int"),
            "Sintomas_disautonomicos": transform_boolean(
                col("Sintomas_disautonomicos")
            ),
            "Sibilancias": transform_boolean(col("Sibilancias")),
            "Soplos": transform_boolean(col("Soplos")),
            "Derrame": transform_boolean(col("Derrame")),
            "Hematologica": transform_boolean(col("Hematologica")),
            "Cardiaca": transform_boolean(col("Cardiaca")),
            "Endocrina": transform_boolean(col("Endocrina")),
            "Gastrointestinal": transform_boolean(col("Gastrointestinal")),
            "Hepatopatia_cronica": transform_boolean(col("Hepatopatia_cronica")),
            "Neurologica": transform_boolean(col("Neurologica")),
            "Pulmonar": transform_boolean(col("Pulmonar")),
            "Renal": transform_boolean(col("Renal")),
            "Trombofilia": transform_boolean(col("Trombofilia")),
            "Urologica": transform_boolean(col("Urologica")),
            "Vascular": transform_boolean(col("Vascular")),
        }
    )

    df = df.withColumn("Otra_Enfermedad", greatest(*DISEASES_CLEANED))

    return df


def transform_ml_data(df: DataFrame) -> DataFrame:
    """
    Transforms the raw data into a format suitable for ML training. Consists of
    discretizing numeric values into intervals and scaling some numeric columns.

    Args:
        df (DataFrame): The raw DataFrame to be transformed.

    Returns:
        DataFrame: A cleaned and transformed DataFrame ready for ML training.
    """
    INF = float("inf")

    # Filling NA values
    df = fill_na_numeric(df)
    df = fill_na_boolean(df)
    df = df.withColumn("Genero", transform_gender(col("Genero")))

    # Scaling numeric values on some columns
    df = df.withColumn(
        "Saturacion_de_la_sangre",
        scale_column(col("Saturacion_de_la_sangre"), 100, 1).astype("int"),
    )
    df = df.withColumn("WBC", scale_column(col("WBC"), 1000).astype("int"))
    df = df.withColumn("PLT", scale_column(col("PLT"), 1000).astype("int"))

    # Converting raw numeric values to intervals
    df = df.withColumns(
        {
            "Edad": eval_interval(
                col("Edad"),
                ((0, 20, 0), (20, 41, 1), (41, 61, 2), (61, 81, 3), (81, INF, 4)),
            ),
            "Frecuencia_respiratoria": eval_interval(
                col("Frecuencia_respiratoria"),
                (
                    (15, 20, 1),
                    (20, 25, 2),
                    (25, 30, 3),
                    (30, 35, 4),
                    (35, 40, 5),
                    (40, 45, 6),
                    (45, 50, 7),
                    (50, 55, 8),
                    (55, 60, 9),
                    (-INF, 15, 10),
                    (60, INF, 11),
                ),
            ),
            "Saturacion_de_la_sangre": eval_interval(
                col("Saturacion_de_la_sangre"),
                (
                    (15, 20, 1),
                    (20, 25, 2),
                    (25, 30, 3),
                    (30, 35, 4),
                    (35, 40, 5),
                    (40, 45, 6),
                    (45, 50, 7),
                    (50, 55, 8),
                    (55, 60, 9),
                    (-INF, 15, 10),
                    (60, INF, 11),
                ),
            ),
            "Frecuencia_cardiaca": eval_interval(
                col("Frecuencia_cardiaca"),
                (
                    (50, 70, 1),
                    (70, 90, 2),
                    (90, 110, 3),
                    (110, 130, 4),
                    (130, 150, 5),
                    (150, 170, 6),
                    (170, 190, 7),
                    (190, 210, 8),
                    (-INF, 50, 9),
                    (210, INF, 10),
                ),
            ),
            "Presion_sistolica": eval_interval(
                col("Presion_sistolica"),
                (
                    (50, 70, 1),
                    (70, 90, 2),
                    (90, 110, 3),
                    (110, 130, 4),
                    (130, 150, 5),
                    (150, 170, 6),
                    (170, 190, 7),
                    (190, 210, 8),
                    (-INF, 50, 9),
                    (210, INF, 10),
                ),
            ),
            "Presion_diastolica": eval_interval(
                col("Presion_diastolica"),
                (
                    (40, 50, 1),
                    (50, 60, 2),
                    (60, 70, 3),
                    (70, 80, 4),
                    (80, 90, 5),
                    (90, 100, 6),
                    (100, 110, 7),
                    (110, 120, 8),
                    (-INF, 40, 9),
                    (120, INF, 10),
                ),
            ),
            "WBC": eval_interval(
                col("WBC"),
                (
                    (2000, 4000, 1),
                    (4000, 10000, 2),
                    (10000, 15000, 3),
                    (15000, 20000, 4),
                    (20000, 30000, 5),
                    (30000, 35000, 6),
                    (-INF, 2000, 7),
                    (35000, INF, 8),
                ),
            ),
            "HB": eval_interval(
                col("HB"),
                (
                    (6, 8, 1),
                    (8, 10, 2),
                    (10, 12, 3),
                    (12, 14, 4),
                    (14, 16, 5),
                    (16, 18, 6),
                    (18, 20, 7),
                    (20, 22, 8),
                    (-INF, 6, 9),
                    (22, INF, 10),
                ),
            ),
            "PLT": eval_interval(
                col("PLT"),
                (
                    (10000, 50000, 1),
                    (50000, 100000, 2),
                    (100000, 150000, 3),
                    (150000, 400000, 4),
                    (400000, 500000, 5),
                    (500000, 600000, 6),
                    (600000, 700000, 7),
                    (-INF, 10000, 8),
                    (700000, INF, 9),
                ),
            ),
        }
    )

    # Updating "Otra Enfermedad" column to reflect new changes on disease columns
    df = df.withColumn("Otra_Enfermedad", greatest(*DISEASES_CLEANED))

    return df
