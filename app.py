from shiny import App, ui
from modulos.datos import cargar_datos
from modulos.tab_perfil import perfil_server, perfil_ui

datos = cargar_datos()

app_ui = ui.page_navbar(
    ui.nav_panel("1. Perfil de la muestra", perfil_ui("perfil")),
    ui.nav_panel("2. Atención, prueba y desenlace", ui.p("En construcción.")),
    ui.nav_panel("3. Edad y comorbilidades", ui.p("En construcción.")),
    ui.nav_panel("4. Evolución temporal", ui.p("En construcción.")),
    title="COVID-19 en México (2020)",
)

def server(input, output, session):
    perfil_server("perfil", datos=datos)

app = App(app_ui, server)