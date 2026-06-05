from utils import eval_interval, proc_boolean, proc_other_diseases
from constants import NUMS, BOOLEANS, DISEASES
from pandas import Series, DataFrame


def fill_na_numeric(df: DataFrame) -> DataFrame:
    """
    Fills NA values in numeric columns with the median value of each column and replaces outliers with the same median value.

    Args:
        df (DataFrame): A DataFrame containing only numeric columns.
    
    Returns:
        DataFrame: A DataFrame with NA values filled and outliers replaced.
    """
    MEDIAN = df.median()
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    RIC = Q3 - Q1
    UPPER_BOUND = Q3 + 1.5*RIC
    LOWER_BOUND = Q1 - 1.5*RIC

    df = df.fillna(MEDIAN)

    # Replacing outliers with median values
    for i in df.columns:
        df[i] = df[i].apply(
            lambda x: x if (x > LOWER_BOUND.loc[i]) and (x<UPPER_BOUND.loc[i]) else MEDIAN.loc[i]
            )

    return df


def fill_na_boolean(df: DataFrame) -> DataFrame:
    """
    Fills NA values in boolean columns with the mode value of each column.

    Args:
        df (DataFrame): A DataFrame containing only boolean columns.

    Returns:
        DataFrame: A DataFrame with NA values filled.
    """
    MODE = df.mode().iloc[0]
    return df.fillna(MODE).astype("int")


def transform_gender(gender: Series) -> Series:
    """
    Transforms the "Género" column from categorical values ("F", "M") to numeric values (0, 1).

    Args:
        gender (Series): A Series containing the "Género" column with categorical values.
    
    Returns:
        Series: A Series with the "Género" column transformed to numeric values.
    """
    female = gender.replace("F|F ", 0, regex=True)
    male = female.replace("M|M ", 1, regex=True)
    return male.astype("int")


def transform_fever(fever: Series) -> Series:
    """
    Transforms the "Fiebre" column from raw values (temperature in Celsius upper or equal to 38 or binary indicator) 
    to a binary indicator (0, 1) where 1 indicates the presence of fever.

    Args:
        fever (Series): A Series containing the "Fiebre" column with raw values.

    Returns:
        Series: A Series with the "Fiebre" column transformed to a binary indicator.
    """
    aux = fever.apply(lambda x: 1 if (x >= 38) or (x == 1) else 0)
    return aux.astype("int")


def scale_column(column: Series, factor: float, upper_bound: float|None = None) -> Series:
    """
    Scales the values in a column by a given factor, with an optional upper bound.

    Args:
        column (Series): A Series containing the column to be scaled.
        factor (float): The factor by which to scale the values.
        upper_bound (float|None): The upper bound for the scaled values. If None, uses the factor as the upper bound.

    Returns:
        Series: A Series with the scaled values.
    """
    if upper_bound is None:
        upper_bound = factor

    return column.apply(lambda x: x * factor if (x>0) and (x<upper_bound) else x)


def transform_other_diseases(data: DataFrame, diseases: list) -> DataFrame | Series:
    """
    Transforms the "Otra Enfermedad" column to reflect the presence of other diseases based on the values in the disease columns.

    Args:
        data (DataFrame): A DataFrame containing the "Otra Enfermedad" column and the disease columns.
        diseases (list): A list of disease column names to check for the presence of other diseases.
    Returns:
        DataFrame | Series: A Series with the "Otra Enfermedad" column transformed to reflect the presence of other diseases.
    """
    return data.apply(proc_other_diseases, axis=1, diseases=diseases)["Otra Enfermedad"]


def transform_boolean(column: Series) -> Series:
    """
    Transforms a boolean column with values like "Sí", "No", "1", "0", etc. to a binary indicator (0, 1).
    Args:
        column (Series): A Series containing the boolean column with raw values.
    Returns:
        Series: A Series with the boolean column transformed to a binary indicator.
    """
    return column.apply(proc_boolean).astype("float")


def transform_to_clean_data(df: DataFrame) -> DataFrame:
    """
    Transforms the raw data into a clean format, it involves filling null values, converting
    qualitative variables to quantitative ones and replacing dirty values with clean ones.

    Args:
        df (DataFrame): The raw DataFrame to be transformed.

    Returns:
        DataFrame: A cleaned and transformed DataFrame ready for analysis or modeling.
    """
    df["Fiebre"] = transform_fever(df["Fiebre"])
    df["HB"] = df["HB"].str.replace(",", ".").astype("float")
    df["PLT"] = df["PLT"].str.replace(",", ".").str.replace("OO", "00").astype("float")

    df["Hemoptisis"] = df["Hemoptisis"].replace("1", 1).replace("0|N0", 0, regex=True).astype("int")
    df["Síntomas disautonomicos"] = transform_boolean(df["Síntomas disautonomicos"])
    df["Sibilancias"] = transform_boolean(df["Sibilancias"])
    df["Soplos"] = transform_boolean(df["Soplos"])
    df["Derrame"] = transform_boolean(df["Derrame"])

    df["Hematologica"] = transform_boolean(df["Hematologica"])
    df["Cardíaca"] = transform_boolean(df["Cardíaca"])
    df["Endocrina"] = transform_boolean(df["Endocrina"])
    df["Gastrointestinal"] = transform_boolean(df["Gastrointestinal"])
    df["Hepatopatía crónica"] = transform_boolean(df["Hepatopatía crónica"])
    df["Neurológica"] = transform_boolean(df["Neurológica"])
    df["Pulmonar"] = transform_boolean(df["Pulmonar"])
    df["Renal"] = transform_boolean(df["Renal"])
    df["Trombofilia"] = transform_boolean(df["Trombofilia"])
    df["Urológica"] = transform_boolean(df["Urológica"])
    df["Vascular"] = transform_boolean(df["Vascular"])

    df["Otra Enfermedad"] = transform_other_diseases(
        df[["Otra Enfermedad"] + DISEASES], DISEASES
    )

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
    df[NUMS] = fill_na_numeric(df[NUMS])
    df[BOOLEANS] = fill_na_boolean(df[BOOLEANS])

    # Scaling numeric values on some columns
    df["Saturación de la sangre"] = scale_column(df["Saturación de la sangre"], 100, upper_bound=1).astype("int")
    df["WBC"] = scale_column(df["WBC"], 1000).astype("int")
    df["PLT"] = scale_column(df["PLT"], 1000).astype("int")

    # Converting raw numeric values to intervals
    df["Edad"] = df["Edad"].apply(eval_interval, intervals=((0, 20, 0), (20, 41, 1), (41, 61, 2), (61, 81, 3), (81, INF, 4)))
    df["Frecuencia respiratoria"] = df["Frecuencia respiratoria"].apply(eval_interval, intervals=((15,20,1),(20,25,2),(25,30,3),(30,35,4),(35,40,5),
                                                                                                  (40,45,6),(45,50,7),(50,55,8),(55,60,9),(-INF,15,10),
                                                                                                  (60,INF,11))).astype("int")
    df["Saturación de la sangre"] = df["Saturación de la sangre"].apply(eval_interval, intervals=((50,55,1),(55,60,2),(60,65,3),(65,70,4),(70,75,5),
                                                                                                  (75,80,6),(80,85,7),(85,90,8),(90,95,9),(95,100,10),(-INF,50,11),
                                                                                                  (100,INF,12))).astype("int")
    df["Frecuencia cardíaca"] = df["Frecuencia cardíaca"].apply(eval_interval, intervals=((50,70,1),(70,90,2),(90,110,3),(110,130,4),(130,150,5),
                                                                                                  (150,170,6),(170,190,7),(190,210,8),(-INF,50,9),
                                                                                                  (210,INF,10))).astype("int")
    df["Presión sistólica"] = df["Presión sistólica"].apply(eval_interval, intervals=((50,70,1),(70,90,2),(90,110,3),(110,130,4),(130,150,5),(150,170,6),
                                                                                       (170,190,7),(190,210,8),(-INF,50,9),(210,INF,10))).astype("int")
    df["Presión diastólica"] = df["Presión diastólica"].apply(eval_interval, intervals=((40,50,1),(50,60,2),(60,70,3),(70,80,4),(80,90,5),(90,100,6),
                                                                                         (100,110,7),(110,120,8),(-INF,40,9),(120,INF,10))).astype("int")
    df["WBC"] = df["WBC"].apply(eval_interval, intervals=((2000,4000,1),(4000,10000,2),(10000,15000,3),(15000,20000,4),(20000,30000,5),(30000,35000,6),
                                                          (-INF,2000,7),(35000,INF,8))).astype("int")
    df["HB"] = df["HB"].apply(eval_interval, intervals=((6,8,1),(8,10,2),(10,12,3),(12,14,4),(14,16,5),(16,18,6),(18,20,7),(20,22,8),(-INF,6,9),(22,INF,10)))
    df["PLT"] = df["PLT"].apply(eval_interval, intervals=((10000,50000,1),(50000,100000,2),(100000,150000,3),(150000,400000,4),(400000,500000,5),(500000,600000,6),
                                                          (600000,700000,7),(-INF,10000,8),(700000,INF,9))).astype("int")
    df["Género"] = transform_gender(df["Género"])

    # Updating "Otra Enfermedad" column to reflect new changes on disease columns
    df["Otra Enfermedad"] = transform_other_diseases(df[["Otra Enfermedad"] + DISEASES], DISEASES)

    return df