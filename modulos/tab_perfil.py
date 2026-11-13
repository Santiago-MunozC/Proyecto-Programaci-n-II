from shiny import module, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from modulos.datos import COMORBILIDADES

@module.ui
def perfil_ui():
    return ui.div(
        ui.h4("Perfil de la muestra"),
        ui.p("¿Cuál es el perfil demográfico y clínico de los pacientes?"),
                ui.div(
            ui.tags.strong("Sobre la muestra: "),
            "los 1,000 registros son una muestra aleatoria estratificada por "
            "tipo de paciente y sexo, no la población completa. Por eso los "
            "porcentajes de esta pestaña describen la muestra y no representan "
            "a México; las proporciones de sexo y de tipo de paciente, en "
            "particular, dependen de cómo se armó la muestra.",
            class_="alert alert-info",
        ),
                ui.accordion(
            ui.accordion_panel(
                "Acerca del conjunto de datos",
                ui.p(
                    "Los datos provienen de la plataforma Kaggle, un repositorio "
                    "público de conjuntos de datos, y corresponden a la información "
                    "abierta sobre casos de COVID-19 publicada por la Secretaría de "
                    "Salud de México en 2020. Cada fila es un paciente anónimo con "
                    "sospecha o diagnóstico de COVID-19."
                ),
                ui.p(
                    "Para este proyecto se eliminaron 28,909 filas con datos "
                    "desconocidos y se tomó una muestra aleatoria estratificada de "
                    "1,000 registros. También se creó la variable FALLECIDO, que vale "
                    "1 si el paciente tiene una fecha de fallecimiento real. El "
                    "conjunto tiene 20 variables y ningún valor nulo."
                ),
                ui.p(ui.tags.strong("Cosas importantes al interpretar los datos:")),
                ui.tags.ul(
                    ui.tags.li(
                        "Solo incluye personas que se hicieron la prueba o recibieron "
                        "atención, así que la mortalidad de la muestra no representa "
                        "la tasa real de mortalidad por COVID-19 en México."
                    ),
                    ui.tags.li(
                        "En las variables de sí/no, 1 = Sí, 2 = No y 97 = No aplica. "
                        "Los 97 no son datos perdidos."
                    ),
                    ui.tags.li(
                        "Hay filas repetidas que no se eliminaron: el conjunto no "
                        "tiene identificador de paciente y casi todas las variables "
                        "son de dos opciones, así que perfiles idénticos aparecen "
                        "de forma natural."
                    ),
                    ui.tags.li(
                        "Algunos grupos son muy pequeños (por ejemplo, 8 embarazadas "
                        "y 12 pacientes con EPOC), y sus porcentajes cambian mucho "
                        "con una sola observación."
                    ),
                ),
            ),
            open=False,
            id="acerca",
        ),
        ui.layout_columns(
            ui.value_box("Pacientes", ui.output_text("n_total")),
            ui.value_box("Hospitalizados", ui.output_text("n_hosp")),
            ui.value_box("Positivos a COVID-19", ui.output_text("n_pos")),
            ui.value_box("Fallecidos", ui.output_text("n_fall")),
            ui.value_box("Edad mediana", ui.output_text("edad_mediana")),
            ui.value_box("Edad media", ui.output_text("edad_media")),
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
        ui.layout_columns(
            ui.card(
                ui.card_header("Tipo de paciente"),
                output_widget("dona_tipo"),
            ),
            ui.card(
                ui.card_header("Resultado de la prueba"),
                output_widget("dona_prueba"),
            ),
        ),
        ui.card(
            ui.card_header("Embarazo (solo entre mujeres)"),
            output_widget("embarazo"),
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

    @render.text
    def edad_mediana():
        return f"{datos["AGE"].median():.0f} años"

    @render.text
    def edad_media():
        return f"{datos["AGE"].mean():.1f} años"

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

    def dona(columna):
        # Cuenta cuántos pacientes hay en cada categoría de la columna
        conteos = datos[columna].value_counts()
        fig = go.Figure(
            go.Pie(
                labels=list(conteos.index),
                values=list(conteos.values),
                hole=0.5,
                textinfo="value+percent",
                sort=False,
            )
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        return fig

    @render_widget
    def dona_tipo():
        return dona("TIPO_PACIENTE")

    @render_widget
    def dona_prueba():
        return dona ("PRUEBA")

    @render_widget
    def embarazo():
        mujeres = datos[datos["SEXO"] == "Mujer"]
        etiquetas = mujeres["PREGNANT"].map({1: "Embarazada", 2: "No embarazada"})
        conteos = etiquetas.value_counts().reindex(["Embarazada", "No embarazada"])

        fig = go.Figure(
            go.Bar(
                x=list(conteos.index),
                y=list(conteos.values),
                text=[f"{n} ({n / len(mujeres):.1%})" for n in conteos.values],
                textposition="outside",
            )
        )
        fig.update_layout(
            yaxis_title= "Número de mujeres",
            yaxis_range=[0, conteos.max() * 1.15],
        )
        return fig