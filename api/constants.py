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