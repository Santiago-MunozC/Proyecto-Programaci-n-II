from shiny import App, ui
from modulos.tab_perfil import perfil_ui

app_ui = ui.page_navbar(
    ui.nav_panel("1. Perfil de la muestra", perfil_ui("perfil")),
    ui.nav_panel("2. Atención, prueba y desenlace", ui.p("En construcción.")),
    ui.nav_panel("3. Edad y comorbilidades", ui.p("En construcción.")),
    ui.nav_panel("4. Evolución temporal", ui.p("En construcción.")),
    title="COVID-19 en México (2020)",
)

def server(input, output, session):
    pass

app = App(app_ui, server)