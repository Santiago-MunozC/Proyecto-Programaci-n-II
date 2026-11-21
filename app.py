from shiny import App, ui

from modulos.datos import cargar_datos
from modulos.tab_atencion import atencion_server, atencion_ui
from modulos.tab_evolucion_temporal import evolucion_temporal_server, evolucion_temporal_ui

from modulos.tab_edad import edad_server, edad_ui
from modulos.tab_perfil import perfil_server, perfil_ui

datos = cargar_datos()

app_ui = ui.page_navbar(
    ui.nav_panel("1. Perfil de la muestra", perfil_ui("perfil")),
    ui.nav_panel("2. Atención, prueba y desenlace", atencion_ui("atencion")),
    ui.nav_panel("3. Edad y comorbilidades", edad_ui("edad")),
    ui.nav_panel("4. Evolución temporal", evolucion_temporal_ui("tiempo")),
    title="COVID-19 en México (2020)",
)

def server(input, output, session):
    perfil_server("perfil", datos=datos)
    atencion_server("atencion", datos=datos)
    evolucion_temporal_server("tiempo", datos=datos)
    edad_server("edad", datos=datos)

app = App(app_ui, server)