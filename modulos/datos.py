from pathlib import Path
import pandas as pd

RUTA_DATOS = Path(__file__).resolve().parent.parent / "covid_muestra_1000.xlsx"

def cargar_datos():
    """Lee el excel y devuelve la tabla de datos"""
    df = pd.read_excel(RUTA_DATOS)
    df["SEXO"] = df["SEX"].map({1: "Mujer", 2: "Hombre"})
    df["TIPO_PACIENTE"] = df["PATIENT_TYPE"].map({1: "Ambulatorio", 2: "Hospitalizado"})
    df["PRUEBA"] = df["COVID_POSITIVO"].map({1: "Positivo", 0: "No positivo"})
    return df