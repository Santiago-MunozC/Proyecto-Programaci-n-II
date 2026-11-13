from pathlib import Path
import pandas as pd

RUTA_DATOS = Path(__file__).resolve().parent.parent / "covid_muestra_1000.xlsx"

# Grupos de edad
CORTES_EDAD = [0, 18, 40, 60, 80, 200]
ETIQUETAS_EDAD = ["0-17", "18-39", "40-59", "60-79", "80+"]

# Comorbilidades
COMORBILIDADES = {
    "DIABETES": "Diabetes",
    "COPD": "Enfermedad pulmonar obstructiva crónica",
    "ASTHMA": "Asma",
    "INMSUPR": "Inmunosupresión",
    "HIPERTENSION": "Hipertensión",
    "OTHER_DISEASE": "Otra enfermedad",
    "CARDIOVASCULAR": "Enfermedad cardiovascular",
    "OBESITY": "Obesidad",
    "RENAL_CHRONIC": "Enfermedad renal crónica",
    "TOBACCO": "Tabaquismo",
}

def cargar_datos():
    """Lee el excel y devuelve la tabla de datos"""
    df = pd.read_excel(RUTA_DATOS)
    df["SEXO"] = df["SEX"].map({1: "Mujer", 2: "Hombre"})
    df["TIPO_PACIENTE"] = df["PATIENT_TYPE"].map({1: "Ambulatorio", 2: "Hospitalizado"})
    df["PRUEBA"] = df["COVID_POSITIVO"].map({1: "Positivo", 0: "No positivo"})
    
    df["GRUPO_EDAD"] = pd.cut(df["AGE"], bins=CORTES_EDAD, labels=ETIQUETAS_EDAD, right=False)
    return df