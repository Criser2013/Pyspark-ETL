from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, StringType
from utils import remove_accents
from re import sub

NUMS = ["Frecuencia respiratoria", "Presión sistólica", "Presión diastólica", "Saturación de la sangre",
        "Frecuencia cardíaca", "WBC", "HB","PLT"]
BOOLEANS = ["Fumador", "Bebedor", "Cirugía reciente", "Inmovilidad de M inferiores",
            "Viaje prolongado", "TEP - TVP Previo", "Malignidad","Disnea","Dolor toracico","Tos","Hemoptisis","Síntomas disautonomicos",
            "Edema de M inferiores", "Crepitaciones","Sibilancias","Soplos","Derrame","Hematologica","Cardíaca","Enfermedad coronaria",
            "Diabetes Mellitus","Endocrina","Gastrointestinal","Hepatopatía crónica","Hipertensión arterial","Neurológica","Pulmonar",
            "Renal","Trombofilia","Urológica","Vascular","VIH"]
DISEASES = ["Hematologica","Cardíaca","Enfermedad coronaria","Diabetes Mellitus","Endocrina","Gastrointestinal",
            "Hepatopatía crónica", "Hipertensión arterial","Neurológica","Pulmonar","Renal","Trombofilia",
            "Urológica","Vascular","VIH"]

NUMS_CLEANED = [remove_accents(sub(r"-|/| ", "_", x)) for x in NUMS]
BOOLEANS_CLEANED = [remove_accents(sub(r"-|/| ", "_", x)) for x in BOOLEANS]
DISEASES_CLEANED = [remove_accents(sub(r"-|/| ", "_", x)) for x in DISEASES]

DTYPES = {
            "Edad": "int", "Frecuencia respiratoria": "int", "WBC": "float", "Saturación de la sangre": "float",
            "Frecuencia cardíaca": "int", "Presión sistólica": "int", "Presión diastólica": "int",
            "HB": "str", "PLT": "str",
            "Género": "str", "Fiebre": "float", "Fumador": "float", "Bebedor": "int",
            "Procedimiento Quirurgicos / Traumatismo Grave en los últimos 15 dias": "float",
            "Inmovilidad de M inferiores": "int", "Viaje prolongado": "float", "TEP - TVP Previo": "float",
            "Malignidad": "int", "Disnea": "int", "Dolor toracico": "int", "Tos": "int",
            "Hemoptisis": "str", "Síntomas disautonomicos": "str", "Edema de M inferiores": "int",
            "Crepitaciones": "int", "Sibilancias": "str", "Soplos": "str", "Derrame": "str",
            "Otra Enfermedad": "str", "Hematologica": "str", "Cardíaca": "str", "Enfermedad coronaria": "float",
            "Diabetes Mellitus": "int", "Endocrina": "str", "Gastrointestinal": "str", "Hepatopatía crónica": "str",
            "Hipertensión arterial": "int", "Neurológica": "str", "Pulmonar": "str", "Renal": "str", 
            "Trombofilia": "str", "Urológica": "str", "Vascular": "str", "VIH": "float", "TEP": "int"
        }

INITIAL_DTYPES = StructType([
    StructField("Edad", StringType(), False),
    StructField("Frecuencia respiratoria", IntegerType(), True),
    StructField("WBC", StringType(), True),
    StructField("Saturación de la sangre", IntegerType(), True),
    StructField("Frecuencia cardíaca", IntegerType(), True),
    StructField("Presión sistólica", IntegerType(), True),
    StructField("Presión diastólica", IntegerType(), True),
    StructField("HB", StringType(), True),
    StructField("PLT", StringType(), True),
    StructField("Género", StringType(), False),
    StructField("Fiebre", FloatType(), True),
    StructField("Fumador", IntegerType(), True),
    StructField("Bebedor", IntegerType(), True),
    StructField("Cirugía reciente", IntegerType(), True),
    StructField("Inmovilidad de M inferiores", IntegerType(), True),
    StructField("Viaje prolongado", IntegerType(), True),
    StructField("TEP - TVP Previo", IntegerType(), True),
    StructField("Malignidad", IntegerType(), True),
    StructField("Disnea", IntegerType(), True),
    StructField("Dolor toracico", IntegerType(), True),
    StructField("Tos", IntegerType(), True),
    StructField("Hemoptisis", StringType(), True),
    StructField("Síntomas disautonomicos", StringType(), True),
    StructField("Edema de M inferiores", IntegerType(), True),
    StructField("Crepitaciones", IntegerType(), True),
    StructField("Sibilancias", StringType(), True),
    StructField("Soplos", StringType(), True),
    StructField("Derrame", StringType(), True),
    StructField("Otra Enfermedad", StringType(), True),
    StructField("Hematologica", StringType(), True),
    StructField("Cardíaca", StringType(), True),
    StructField("Enfermedad coronaria", IntegerType(), True),
    StructField("Diabetes Mellitus", IntegerType(), True),
    StructField("Endocrina", StringType(), True),
    StructField("Gastrointestinal", StringType(), True),
    StructField("Hepatopatía crónica", StringType(), True),
    StructField("Hipertensión arterial", IntegerType(), True),
    StructField("Neurológica", StringType(), True),
    StructField("Pulmonar", StringType(), True),
    StructField("Renal", StringType(), True),
    StructField("Trombofilia", StringType(), True),
    StructField("Urológica", StringType(), True),
    StructField("Vascular", StringType(), True),
    StructField("VIH", IntegerType(), True),
    StructField("TEP", IntegerType(), False)
])