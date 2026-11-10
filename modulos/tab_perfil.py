from shiny import module, render, ui

@module.ui
def perfil_ui():
    return ui.div(
        ui.h4("Perfil de la muestra"),
        ui.p("¿Cuál es el perfil demográfico y clínico de los pacientes?"),
        ui.layout_columns(
            ui.value_box("Pacientes", ui.output_text("n_total")),
            ui.value_box("Hospitalizados", ui.output_text("n_hosp")),
            ui.value_box("Positivos a COVID-19", ui.output_text("n_pos")),
            ui.value_box("Fallecidos", ui.output_text("n_fall")),
            fill=False,
        ),
    )

@module.server
def perfil_server(input, output, session, datos):

    def con_porcentaje(n):
        return f"{n:,} ({n / len(datos):.1%})"

    @render.text
    def n_total():
        return f"{len(datos):,}"

    @render.text
    def n_hosp():
        return con_porcentaje(int((datos["PATIENT_TYPE"] == 2).sum()))

    @render.text
    def n_pos():
        return con_porcentaje(int(datos["COVID_POSITIVO"].sum()))

    @render.text
    def n_fall():
        return con_porcentaje(int(datos["FALLECIDO"].sum()))