from shiny import module, ui

@module.ui
def atencion_ui():
    return ui.div(
        ui.h4("Atención médica, prueba y desenlace"),
        ui.p(
            "¿Cómo cambia la proporción de fallecidos según el tipo de atención, el resultado de la prueba y el sexo, y cómo se asocia la gravedad clínica con el fallecimiento?",
            class_="text-muted",
        ),
    )

@module.server
def atencion_server(input, output, session, datos):
    pass