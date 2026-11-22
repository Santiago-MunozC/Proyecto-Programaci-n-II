import plotly.io as pio
from shiny import App, ui

from modulos.datos import cargar_datos
from modulos.tab_atencion import atencion_server, atencion_ui
from modulos.tab_edad import edad_server, edad_ui
from modulos.tab_evolucion_temporal import (
    evolucion_temporal_server,
    evolucion_temporal_ui,
)
from modulos.tab_perfil import perfil_server, perfil_ui

pio.templates.default = "plotly_white"
pio.templates["plotly_white"].layout.font.family = "Inter, sans-serif"  # misma fuente en los gráficos 

ESTILO = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* ---- Base de toda la app ---- */
body { font-family: 'Inter', sans-serif; background-color: #f5f7fb; }

/* ---- Barra superior: título grande y pestañas ---- */
.navbar {
    background-color: #1f3a5f !important;
    padding-top: 0.6rem;
    padding-bottom: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
.navbar-brand {
    color: #ffffff !important;
    font-size: 1.7rem;
    font-weight: 700;
    margin-right: 2rem;
}
.navbar .nav-link {
    color: rgba(255, 255, 255, 0.75) !important;
    font-weight: 600;
    padding: 0.8rem 1.1rem;
    border-bottom: 4px solid transparent;
}
.navbar .nav-link:hover { color: #ffffff !important; }
.navbar .nav-link.active {
    color: #ffffff !important;
    background-color: transparent !important;
    border-bottom: 4px solid #EF553B;
}

/* ---- Títulos de cada pestaña ---- */
h4 {
    font-weight: 700;
    color: #1f3a5f;
    border-bottom: 3px solid #636EFA;
    padding-bottom: 0.3rem;
    margin-bottom: 0.75rem;
}

/* ---- Tarjetas ---- */
.card {
    border: none;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(31, 58, 95, 0.08);
}
.card-header { font-weight: 600; background-color: #f1f4fb; }
.accordion { margin-bottom: 1rem; }
.alert { border-radius: 8px; }
.text-muted { font-size: 0.92rem; }
"""


datos = cargar_datos()

app_ui = ui.page_navbar(
    ui.nav_panel("1. Perfil de la muestra", perfil_ui("perfil")),
    ui.nav_panel("2. Atención, prueba y desenlace", atencion_ui("atencion")),
    ui.nav_panel("3. Edad y comorbilidades", edad_ui("edad")),
    ui.nav_panel("4. Evolución temporal", evolucion_temporal_ui("tiempo")),
    title="COVID-19 en México (2020)",
    header=ui.tags.style(ESTILO),
)

def server(input, output, session):
    perfil_server("perfil", datos=datos)
    atencion_server("atencion", datos=datos)
    evolucion_temporal_server("tiempo", datos=datos)
    edad_server("edad", datos=datos)

app = App(app_ui, server)