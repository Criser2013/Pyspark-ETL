from utils import eval_interval
from constants import NUMS, BOOLEANS, DISEASES
from pyspark.sql import DataFrame, Column
from pyspark.sql.functions import transform, replace, lower, when, greatest, mode, trim, median, percentile


def fill_na_numeric(col: Column) -> Column:
    """
    Fills NA values in numeric columns with the median value of each column and replaces outliers with the same median value.

    Args:
        col (Column): Column to be imputed.
    
    Returns:
        Column: A Column with NA values filled and outliers replaced.
    """
    MEDIAN = median(col)
    Q1 = percentile(col, 0.25)
    Q3 = percentile(col, 0.75)
    RIC = Q3 - Q1
    UPPER_BOUND = Q3 + 1.5*RIC
    LOWER_BOUND = Q1 - 1.5*RIC

    col = col.when(col.isNull(), MEDIAN).otherwise(col)
    col = col.when((col < LOWER_BOUND) | (col > UPPER_BOUND), MEDIAN).otherwise(col)

    return col


def fill_na_boolean(col: Column) -> Column:
    """
    Fills NA values in boolean columns with the mode value of each column.

    Args:
        col (Column): Column to be imputed.

    Returns:
        Column: A Column with NA values filled.
    """
    MODE = mode(col)
    return col.when(col.isNull(), MODE).otherwise(col)


def transform_gender(gender: Column) -> Column:
    """
    Transforms the "Género" column from categorical values ("F", "M") to numeric values (0, 1).

    Args:
        gender (Column): A Column containing the "Género" column with categorical values.
    
    Returns:
        Column: A Column with the "Género" column transformed to numeric values.
    """
    gender_lower = lower(trim(gender))
    male = replace(gender_lower, "m", "1")
    female = replace(male, "f", "0")
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
    return fever.when((fever >= 38) | (fever == 1), 1).otherwise(0)


def scale_column(column: Column, factor: float, upper_bound: float|None = None) -> Column:
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

    return column.when(
        (column > 0) & (column < upper_bound), column * factor
        ).otherwise(column)


def transform_boolean(data: Column) -> Column:
    """
    Transforms a string representing a boolean value into an integer (1 or 0). Treats common placeholders as NA.

    Args:
        data (Column): The column to transform.
    
    Returns:
        Column: 1 for true values, 0 for false values.
    """
    data = lower(trim(data))
    data = data.transform(lambda x: when(x.isin("1", "0"), x).when(x.isin("ni", "no", "n"), "0").otherwise("1"))
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
    df = df.withColumns({
        "Fiebre": transform(replace("Fiebre", ",", ".").cast("float"), transform_fever),
        "WBC": replace("WBC", ",", ".").cast("float"),
        "HB": replace("HB", ",", ".").cast("float"),
        "PLT": replace(replace("PLT", ",", "."), "OO", "00").cast("float"),
        "Hemoptisis": replace("Hemoptisis", "N0", "0").cast("int"),
        "Síntomas disautonomicos": transform("Síntomas disautonomicos", transform_boolean),
        "Sibilancias": transform("Sibilancias", transform_boolean),
        "Soplos": transform("Soplos", transform_boolean),
        "Derrame": transform("Derrame", transform_boolean),
        "Hematologica": transform("Hematologica", transform_boolean),
        "Cardíaca": transform("Cardíaca", transform_boolean),
        "Endocrina": transform("Endocrina", transform_boolean),
        "Gastrointestinal": transform("Gastrointestinal", transform_boolean),
        "Hepatopatía crónica": transform("Hepatopatía crónica", transform_boolean),
        "Neurológica": transform("Neurológica", transform_boolean),
        "Pulmonar": transform("Pulmonar", transform_boolean),
        "Renal": transform("Renal", transform_boolean),
        "Trombofilia": transform("Trombofilia", transform_boolean),
        "Urológica": transform("Urológica", transform_boolean),
        "Vascular": transform("Vascular", transform_boolean),
    })

    df = df.withColumn("Otra Enfermedad", greatest(*DISEASES))

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
    mapper = { f"{i}": transform(i, fill_na_numeric) for i in NUMS }

    for i in BOOLEANS:
        mapper[i] = transform(i, fill_na_boolean)

    mapper["Género"] = transform("Género", transform_gender)

    df = df.withColumns(mapper)

    # Scaling numeric values on some columns
    df = df.withColumn("Saturación de la sangre", scale_column(df["Saturación de la sangre"], 100, 1).astype("int"))
    df = df.withColumn("WBC", scale_column(df["WBC"], 1000).astype("int"))
    df = df.withColumn("PLT", scale_column(df["PLT"], 1000).astype("int"))

    # Converting raw numeric values to intervals
    df = df.withColumns({
        "Edad": eval_interval(df["Edad"], ((0, 20, 0), (20, 41, 1), (41, 61, 2), (61, 81, 3), (81, INF, 4))),
        "Frecuencia respiratoria": eval_interval(df["Frecuencia respiratoria"], ((15,20,1),(20,25,2),(25,30,3),(30,35,4),(35,40,5),
                                                                                 (40,45,6),(45,50,7),(50,55,8),(55,60,9),(-INF,15,10),
                                                                                 (60,INF,11))),
        "Saturación de la sangre": eval_interval(df["Saturación de la sangre"], ((15,20,1),(20,25,2),(25,30,3),(30,35,4),(35,40,5),
                                                                                 (40,45,6),(45,50,7),(50,55,8),(55,60,9),(-INF,15,10),
                                                                                 (60,INF,11))),
        "Frecuencia cardíaca": eval_interval(df["Frecuencia cardíaca"], ((50,70,1),(70,90,2),(90,110,3),(110,130,4),(130,150,5),
                                                                         (150,170,6),(170,190,7),(190,210,8),(-INF,50,9),
                                                                         (210,INF,10))),
        "Presión sistólica": eval_interval(df["Presión sistólica"], ((50,70,1),(70,90,2),(90,110,3),(110,130,4),(130,150,5),(150,170,6),
                                                                     (170,190,7),(190,210,8),(-INF,50,9),(210,INF,10))),
        "Presión diastólica": eval_interval(df["Presión diastólica"], ((40,50,1),(50,60,2),(60,70,3),(70,80,4),(80,90,5),(90,100,6),
                                                                       (100,110,7),(110,120,8),(-INF,40,9),(120,INF,10))),
        "WBC": eval_interval(df["WBC"], ((2000,4000,1),(4000,10000,2),(10000,15000,3),(15000,20000,4),(20000,30000,5),(30000,35000,6),
                                         (-INF,2000,7),(35000,INF,8))),
        "HB": eval_interval(df["HB"], ((6,8,1),(8,10,2),(10,12,3),(12,14,4),(14,16,5),(16,18,6),(18,20,7),(20,22,8),(-INF,6,9),(22,INF,10))),
        "PLT": eval_interval(df["PLT"], ((10000,50000,1),(50000,100000,2),(100000,150000,3),(150000,400000,4),(400000,500000,5),(500000,600000,6),
                                         (600000,700000,7),(-INF,10000,8),(700000,INF,9)))
    })

    # Updating "Otra Enfermedad" column to reflect new changes on disease columns
    df = df.withColumn("Otra Enfermedad", greatest(*DISEASES))

    return df