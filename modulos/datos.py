from pathlib import Path
import pandas as pd

RUTA_DATOS = Path(__file__).resolve().parent.parent / "covid_muestra_1000.xlsx"

def cargar_datos():
    """Lee el excel y devuelve la tabla de datos"""
    df = pd.read_excel(RUTA_DATOS)
    return df