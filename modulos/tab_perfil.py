from shiny import module, ui

@module.ui
def perfil_ui():
    return ui.div(
        ui.h4("Perfil de la muestra"),
        ui.p("Cuál es el perfil demográfico y clínico de los pacientes?"),
    )