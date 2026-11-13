from shiny import module, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from modulos.datos import COMORBILIDADES

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
        ui.card(
            ui.card_header("Pirámide poblacional"),
            output_widget("piramide"),
        ),
        ui.card(
            ui.card_header("Prevalencia de comorbilidades"),
            output_widget("comorbilidades"),
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

    @render_widget
    def piramide():
        # Cuenta pacientes por grupo de edad y sexo
        tabla = datos.groupby(["GRUPO_EDAD", "SEXO"], observed=False).size().unstack()

        maximo = int(tabla.max().max())
        tope = ((maximo // 50) + 1) * 50
        marcas = list(range(-tope, tope + 1, 50))

        fig = go.Figure()
        fig.add_bar(
            y=tabla.index.astype(str), x=-tabla["Hombre"], name="Hombre",
            orientation="h", customdata=tabla["Hombre"],
            hovertemplate="Hombres: %{customdata}<extra></extra>",
        )
        fig.add_bar(
            y=tabla.index.astype(str), x=tabla["Mujer"], name="Mujer",
            orientation="h",
            hovertemplate="Mujeres: %{x}<extra></extra>",

        )
        fig.update_layout(
            barmode="relative",
            xaxis=dict(
                tickvals=marcas,
                ticktext=[str(abs(m)) for m in marcas],
                title="Número de pacientes",
            ),
            yaxis_title="Grupo de edad",
        )
        return fig

    @render_widget
    def comorbilidades():
        # Cuenta cuántos pacientes tienen cada comorbilidad
        conteos = {
            nombre: int((datos[columna] == 1). sum())
            for columna, nombre in COMORBILIDADES.items()
        }

        orden = sorted(conteos, key=conteos.get)
        porcentajes = [conteos[n] / len(datos) * 100 for n in orden]

        fig = go.Figure(
            go.Bar(
                x=porcentajes,
                y=orden,
                orientation="h",
                text=[f"{conteos[n] / len(datos):.1%} (n = {conteos[n]})" for n in orden],
                textposition="outside",
                hoverinfo="skip",
            )
        )
        fig.update_layout(
            xaxis_title="% de pacientes",
            xaxis_range=[0, max(porcentajes) * 1.4],
            margin=dict(l=180),
        )
        return fig