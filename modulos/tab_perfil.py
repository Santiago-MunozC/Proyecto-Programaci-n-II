from shiny import module, reactive, render, ui
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
            "los 1,000 registros son una muestra aleatoria estratificada por tipo de paciente y sexo, no la población completa. Por eso los porcentajes de esta pestaña describen la muestra y no representan a México; las proporciones de sexo y de tipo de paciente, en particular, dependen de cómo se armó la muestra.",
            class_="alert alert-info",
        ),
                ui.accordion(
            ui.accordion_panel(
                "Acerca del conjunto de datos",
                ui.p(
                    "Los datos provienen de la plataforma Kaggle, un repositorio público de conjuntos de datos, y corresponden a la información abierta sobre casos de COVID-19 publicada por la Secretaría de Salud de México en 2020. Cada fila es un paciente anónimo con sospecha o diagnóstico de COVID-19."
                ),
                ui.p(
                    "Para este proyecto se eliminaron 28,909 filas con datos desconocidos y se tomó una muestra aleatoria estratificada de 1,000 registros. También se creó la variable FALLECIDO, que vale 1 si el paciente tiene una fecha de fallecimiento real. El conjunto tiene 20 variables y ningún valor nulo."
                ),
                ui.p(ui.tags.strong("Cosas importantes al interpretar los datos:")),
                ui.tags.ul(
                    ui.tags.li(
                        "Solo incluye personas que se hicieron la prueba o recibieron atención, así que la mortalidad de la muestra no representa la tasa real de mortalidad por COVID-19 en México."
                    ),
                    ui.tags.li(
                        "En las variables de sí/no, 1 = Sí, 2 = No y 97 = No aplica. Los 97 no son datos perdidos."
                    ),
                    ui.tags.li(
                        "Hay filas repetidas que no se eliminaron: el conjunto no tiene identificador de paciente y casi todas las variables son de dos opciones, así que perfiles idénticos aparecen de forma natural."
                    ),
                    ui.tags.li(
                        "Algunos grupos son muy pequeños (por ejemplo, 8 embarazadas y 12 pacientes con EPOC), y sus porcentajes cambian mucho con una sola observación."
                    ),
                ),
            ),
            open=False,
            id="acerca",
        ),
                ui.card(
            ui.card_header("Filtros"),
            ui.layout_columns(
                ui.input_select("sexo", "Sexo", ["Todos", "Mujer", "Hombre"]),
                ui.input_select(
                    "tipo", "Tipo de paciente",
                    ["Todos", "Ambulatorio", "Hospitalizado"],
                ),
            ),
            ui.p(
                "Los filtros actualizan las tarjetas y los gráficos. Los comentarios en gris describen la muestra completa.",
                class_="text-muted",
            ),
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
                        ui.p(
                "La muestra es relativamente joven: 455 de los 1,000 pacientes (45.5%) tienen entre 18 y 39 años y solo 139 (13.9%) tienen 60 años o más. Hombres y mujeres están prácticamente en partes iguales (501 y 499), algo esperable porque la muestra se estratificó por sexo.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Prevalencia de comorbilidades"),
            output_widget("comorbilidades"),
                        ui.p(
                "Las comorbilidades más frecuentes son la obesidad (14.7%), la hipertensión (14.6%) y la diabetes (10.9%); el tabaquismo llega a 7.9% y las demás quedan por debajo del 4%. En total, 383 pacientes tienen al menos una comorbilidad y 617 no tienen ninguna. En los grupos pequeños, como los 12 casos de EPOC, los porcentajes son poco estables.",
                class_="text-muted",
            ),
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header("Tipo de paciente"),
                output_widget("dona_tipo"),
                                ui.p(
                    "Alrededor de cuatro de cada cinco pacientes (815, el 81.5%) fueron ambulatorios y 185 (18.5%) fueron hospitalizados. Esta proporción depende de cómo se armó la muestra, así que no representa la de la población.",
                    class_="text-muted",
                ),
            ),
            ui.card(
                ui.card_header("Resultado de la prueba"),
                output_widget("dona_prueba"),
                                ui.p(
                    "372 pacientes (37.2%) dieron positivo a COVID-19 y 628 (62.8%) no. La categoría No positivo incluye resultados negativos y no concluyentes.",
                    class_="text-muted",
                ),
            ),
        ),
        ui.card(
            ui.card_header("Embarazo (solo entre mujeres)"),
            output_widget("embarazo"),
                        ui.p(
                "Solo 8 de las 499 mujeres (1.6%) estaban embarazadas. Con tan pocos casos, cualquier porcentaje calculado sobre este grupo cambia mucho con una sola observación, por lo que debe interpretarse con cuidado.",
                class_="text-muted",
            ),
        ),
    )

@module.server
def perfil_server(input, output, session, datos):

    @reactive.calc
    def datos_filtrados():
        # Aplica los filtros elegidos por el usuario a la tabla completa
        df = datos
        if input.sexo() != "Todos":
            df = df[df["SEXO"] == input.sexo()]
        if input.tipo() != "Todos":
            df = df[df["TIPO_PACIENTE"] == input.tipo()]
        return df

    def con_porcentaje(n, total):
        return f"{n:,} ({n / len(datos):.1%})"

    @render.text
    def n_total():
        return f"{len(datos_filtrados()):,}"

    @render.text
    def n_hosp():
        df = datos_filtrados()
        return con_porcentaje(int((df["PATIENT_TYPE"] == 2).sum()), len(df))

    @render.text
    def n_pos():
        df = datos_filtrados()
        return con_porcentaje(int(df["COVID_POSITIVO"].sum()), len (df))

    @render.text
    def n_fall():
        df = datos_filtrados()
        return con_porcentaje(int(df["FALLECIDO"].sum()), len(df))

    @render.text
    def edad_mediana():
        return f"{datos_filtrados()["AGE"].median():.0f} años"

    @render.text
    def edad_media():
        return f"{datos_filtrados()["AGE"].mean():.1f} años"

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