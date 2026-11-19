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


