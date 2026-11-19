import pandas as pd
from shiny import module, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from modulos.datos import COMORBILIDADES, ETIQUETAS_EDAD

AZUL = "#636EFA"
ROJO = "#EF553B"
PALETA = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
          "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
COLOR_BARRAS = ROJO
COLOR_ACUM = AZUL
COLOR_LINEA = AZUL
COLOR_POCOS = "#B0B0B0"
MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


APILAR = {
    "GRUPO_EDAD": "Grupo de edad",
    "TIPO_PACIENTE": "Tipo de paciente",
    "SEXO": "Sexo",
    "PRUEBA": "Resultado de la prueba",
    "N_COMORB_CAT": "Número de comorbilidades",
}
CATEGORIAS = {
    "GRUPO_EDAD": ETIQUETAS_EDAD,
    "TIPO_PACIENTE": ["Ambulatorio", "Hospitalizado"],
    "SEXO": ["Hombre", "Mujer"],
    "PRUEBA": ["Positivo", "No positivo"],
    "N_COMORB_CAT": ["0", "1", "2", "3 o más"],
}

COLORES = {
    "GRUPO_EDAD": PALETA[:len(ETIQUETAS_EDAD)],
    "TIPO_PACIENTE": [AZUL, ROJO],
    "SEXO": [AZUL, ROJO],
    "PRUEBA": [ROJO, AZUL],
    "N_COMORB_CAT": PALETA[:4],
}

INDICADORES = {
    "edad": "Edad mediana (años)",
    "hombres": "% de hombres",
    "comorb": "% con al menos una comorbilidad",
    "hosp": "% hospitalizados",
    "positivo": "% con prueba positiva",
}


def _etiqueta_mes(f):
    return f"{MESES[f.month]} {f.year}"

def _fecha_corta(f):
    return f"{f.day} {MESES[f.month]} {f.year}"

def _valor(sub, clave):
    """Valor de un indicador para un grupo de fallecidos (None si el grupo está vacío)."""
    if len(sub) == 0:
        return None
    if clave == "edad":
        return float(sub["AGE"].median())
    if clave == "hombres":
        return float((sub["SEXO"] == "Hombre").mean() * 100)
    if clave == "comorb":
        return float((sub["N_COMORB"] > 0).mean() * 100)
    if clave == "hosp":
        return float((sub["TIPO_PACIENTE"] == "Hospitalizado").mean() * 100)
    return float((sub["PRUEBA"] == "Positivo").mean() * 100)  # positivo

def _indicador_por_mes(df, meses, clave):
    """Para cada mes devuelve cuántos fallecidos hay (n) y el valor del indicador."""
    filas = []
    for m in meses:
        sub = df[df["MES"] == m]
        filas.append({"MES": m, "n": len(sub), "valor": _valor(sub, clave)})
    return pd.DataFrame(filas)

def _tabla_burbujas(df, meses):
    """Una fila por mes y comorbilidad, con los fallecidos acumulados hasta ese mes."""
    filas = []
    for m in meses:
        acum = df[df["MES"] <= m]
        n_total = len(acum)
        for columna, nombre in COMORBILIDADES.items():
            sub = acum[acum[columna] == 1]
            n = len(sub)
            filas.append({
                "MES": m, "comorbilidad": nombre, "n": n, "n_total": n_total,
                "pct": n / n_total * 100 if n else None,
                "edad": float(sub["AGE"].median()) if n else None,
            })
    return pd.DataFrame(filas)

def _tabla_apilada(df, meses, variable):
    categorias = CATEGORIAS[variable]
    return (
        df.groupby(["MES", variable], observed=False)
        .size()
        .unstack(fill_value=0)
        .reindex(index=meses, columns=categorias, fill_value=0)
    )
