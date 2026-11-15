from shiny import module, ui
from shinywidgets import output_widget, render_widget
import plotly.express as px
import plotly.graph_objects as go

@module.ui
def atencion_ui():
    return ui.div(
        ui.h4("Atención médica, prueba y desenlace"),
        ui.p(
            "¿Cómo cambia la proporción de fallecidos según el tipo de atención, el resultado de la prueba y el sexo, y cómo se asocia la gravedad clínica con el fallecimiento?",
            class_="text-muted",
        ),
        ui.div(
            ui.tags.strong("Ojo con los grupos pequeños: "),
            "en toda la muestra hay solo 69 fallecidos (4 entre los 815 pacientes ambulatorios y ninguno entre las 8 embarazadas). Con tan pocos casos, un porcentaje puede cambiar mucho por una sola persona, por eso cada barra muestra también el número de pacientes. Además, estos porcentajes describen la muestra y no son tasas de mortalidad en México.",
            class_="alert alert-warning",
        ),
        ui.card(
            ui.card_header("Fallecidos según tipo de atención, prueba y sexo"),
            output_widget("barras_tipo_prueba"),
                        ui.p("Entre los ambulatorios casi no hay fallecimientos: solo 4 de 815, todos hombres con prueba positiva (4 de 142, el 2.8%); ninguna de las 424 mujeres ambulatorias falleció. Entre los hospitalizados el porcentaje es mucho más alto (35.1% en total) y, en ambos sexos, mayor entre los positivos que entre los no positivos: 43.6% contra 22.2% en mujeres y 39.3% contra 32.7% en hombres. Los grupos de hospitalizados tienen entre 36 y 61 pacientes, así que las diferencias entre ellos deben tomarse con cautela.",
                class_="text-muted",
            ),
            ui.p(
                "Cada barra muestra el porcentaje de fallecidos y, entre paréntesis, los fallecidos sobre el total de pacientes del grupo. Los grupos con pocos pacientes dan porcentajes poco estables.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Fallecidos con y sin neumonía, según la prueba"),
            output_widget("barras_neumonia"),
                        ui.p("Los pacientes con neumonía tienen un porcentaje de fallecidos mucho mayor que los que no la tienen: 37.0% (50 de 135) contra 2.2% (19 de 865) en total. La diferencia se mantiene en ambos resultados de la prueba: 27.9% contra 1.2% entre los no positivos y 44.6% contra 4.0% entre los positivos. Esto es una asociación en la muestra y no demuestra que la neumonía sea la causa del fallecimiento.",
                class_="text-muted",
            ),
            ui.p(
                "Cada barra muestra el porcentaje de fallecidos y, entre paréntesis, los fallecidos sobre el total de pacientes del grupo.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Fallecidas entre embarazadas y no embarazadas"),
            output_widget("barras_embarazo"),
                        ui.p("Ninguna de las 8 embarazadas falleció, frente a 25 de las 491 mujeres no embarazadas (5.1%). Con solo 8 casos, ese 0% no permite concluir que el embarazo se asocie con menor mortalidad.",
                class_="text-muted",
            ),
            ui.p("Solo se incluyen mujeres, porque en los hombres la variable no aplica. Hay apenas 8 embarazadas en la muestra, así que este resultado no permite concluir si el embarazo se asocia con el fallecimiento",
            class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Recorrido de los pacientes: atención, unidad de cuidados intensivos, intubación y desenlace"),
            output_widget("sankey"),
                        ui.p("Los 815 ambulatorios no pasan por cuidados intensivos ni intubación. De los 185 hospitalizados, 15 ingresaron a cuidados intensivos (8 fallecieron) y 25 fueron intubados (22 fallecieron, el 88%). Entre los 160 hospitalizados que no fueron intubados fallecieron 43 (26.9%). Además, 18 de los 25 intubados no pasaron por cuidados intensivos. Son grupos pequeños, y los tratamientos más intensivos se dan a los pacientes más graves, así que esto no debe leerse como que el tratamiento causa el fallecimiento.",
                class_="text-muted",
            ),
            ui.p("El ancho de cada franja es el número de pacientes. Los pacientes ambulatorios no pasan por cuidados intensivos ni intubación, por eso aparecen en No aplica. Cuidados intensivos e intubación solo existen en los hospitalizados.",
            class_="text-muted",
            ),
        ),
    )

@module.server
def atencion_server(input, output, session, datos):
    @render_widget
    def barras_tipo_prueba():
        tabla = (
            datos.groupby(["SEXO", "TIPO_PACIENTE", "PRUEBA"], observed=False)["FALLECIDO"]
            .agg(fallecidos="sum", total="count")
            .reset_index()
        )
        tabla["porcentaje"] = tabla["fallecidos"] / tabla["total"] * 100
        tabla["texto"] = tabla.apply(
            lambda f: f"{f["porcentaje"]:.1f}% ({int(f["fallecidos"])} de {int(f["total"])})",
            axis=1,
        )

        fig = px.bar(
            tabla,
            x="TIPO_PACIENTE",
            y="porcentaje",
            color="PRUEBA",
            barmode="group",
            facet_col="SEXO",
            text="texto",
            category_orders={
                "SEXO": ["Mujer", "Hombre"],
                "TIPO_PACIENTE": ["Ambulatorio", "Hospitalizado"],
                "PRUEBA": ["No positivo", "Positivo"],
            },
            labels={
                "porcentaje": "% de fallecidos",
                "TIPO_PACIENTE": "Tipo de paciente",
                "PRUEBA": "Resultado de la prueba",
                "SEXO": "Sexo",
            },
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, tabla["porcentaje"].max() * 1.3])
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        return fig

    @render_widget
    def barras_neumonia():
        df = datos.copy()
        df["NEUMONIA"] = df["PNEUMONIA"].map({1: "Con neumonía", 2: "Sin neumonía"})

        tabla = (
            df.groupby(["NEUMONIA", "PRUEBA"], observed=False)["FALLECIDO"]
            .agg(fallecidos="sum", total="count")
            .reset_index()
        )
        tabla["porcentaje"] = tabla["fallecidos"] / tabla["total"] * 100
        tabla["texto"] = tabla.apply(
            lambda f: f"{f["porcentaje"]:.1f}% ({int(f["fallecidos"])} de {int(f["total"])})",
            axis=1,
        )

        fig = px.bar(
            tabla,
            x="NEUMONIA",
            y="porcentaje",
            color="PRUEBA",
            barmode="group",
            text="texto",
            category_orders={
                "NEUMONIA": ["Sin neumonía", "Con neumonía"],
                "PRUEBA": ["No positivo", "Positivo"],
            },
            labels={
                "porcentaje": "% de fallecidos",
                "NEUMONIA": "Neumonía",
                "PRUEBA": "Resultado de la prueba",
            },
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, tabla["porcentaje"].max() * 1.3])
        return fig

    @render_widget
    def barras_embarazo():
        mujeres = datos[datos["SEXO"] == "Mujer"].copy()
        mujeres["EMBARAZO"] = mujeres["PREGNANT"].map(
            {1: "Embarazada", 2: "No embarazada"}
        )

        tabla = (
            mujeres.groupby("EMBARAZO", observed=False)["FALLECIDO"]
            .agg(fallecidos="sum", total="count")
            .reset_index()
        )
        tabla["porcentaje"] = tabla["fallecidos"] / tabla["total"] * 100
        tabla["texto"] = tabla.apply(
            lambda f: f"{f['porcentaje']:.1f}% ({int(f['fallecidos'])} de {int(f['total'])})",
            axis=1,
        )

        fig = px.bar(
            tabla,
            x="EMBARAZO",
            y="porcentaje",
            text="texto",
            category_orders={"EMBARAZO": ["No embarazada", "Embarazada"]},
            labels={"porcentaje": "% de fallecidas", "EMBARAZO": "Estado"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, max(tabla["porcentaje"].max() * 1.3, 5)])
        return fig

    @render_widget
    def sankey():
        df = datos.copy()
        df["Tipo"] = df["TIPO_PACIENTE"]
        df["UCI"] = df["ICU"].map(
            {
                1: "Cuidados intensivos: Sí",
                2: "Cuidados intensivos: No",
                97: "Cuidados intensivos: No aplica",
            }
        )
        df["Intubación"] = df["INTUBED"].map(
            {1: "Intubación: Sí", 2: "Intubación: No", 97: "Intubación: No aplica"}
        )
        df["Desenlace"] = df["FALLECIDO"].map({1: "Fallecido", 0: "Sobreviviente"})

        columnas = ["Tipo", "UCI", "Intubación", "Desenlace"]
        nodos = [
            "Ambulatorio", "Hospitalizado",
            "Cuidados intensivos: Sí", "Cuidados intensivos: No",
            "Cuidados intensivos: No aplica",
            "Intubación: Sí", "Intubación: No", "Intubación: No aplica",
            "Fallecido", "Sobreviviente",
        ]
        posicion = {nombre: i for i, nombre in enumerate(nodos)}
        origen, destino, valor = [], [], []
        for a, b in zip(columnas[:-1], columnas[1:]):
            for (desde, hacia), n in df.groupby([a, b]).size().items():
                origen.append(posicion[desde])
                destino.append(posicion[hacia])
                valor.append(int(n))

        fig = go.Figure(
            go.Sankey(
                node=dict(
                    label=nodos,
                    pad=20,
                    thickness=20,
                    hovertemplate="%{label}<br>Pacientes: %{value:,.0f}<extra></extra>",
                ),
                link=dict(
                    source=origen,
                    target=destino,
                    value=valor,
                    hovertemplate=(
                        "%{source.label} → %{target.label}"
                        "<br>Pacientes: %{value:,.0f}<extra></extra>"
                    ),
                ),
            )
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        return fig