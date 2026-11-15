from shiny import module, ui
from shinywidgets import output_widget, render_widget
import plotly.express as px

@module.ui
def atencion_ui():
    return ui.div(
        ui.h4("Atención médica, prueba y desenlace"),
        ui.p(
            "¿Cómo cambia la proporción de fallecidos según el tipo de atención, el resultado de la prueba y el sexo, y cómo se asocia la gravedad clínica con el fallecimiento?",
            class_="text-muted",
        ),
        ui.card(
            ui.card_header("Fallecidos según tipo de atención, prueba y sexo"),
            output_widget("barras_tipo_prueba"),
            ui.p(
                "Cada barra muestra el porcentaje de fallecidos y, entre paréntesis, los fallecidos sobre el total de pacientes del grupo. Los grupos con pocos pacientes dan porcentajes poco estables.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Fallecidos con y sin neumonía, según la prueba"),
            output_widget("barras_neumonia"),
            ui.p(
                "Cada barra muestra el porcentaje de fallecidos y, entre paréntesis, los fallecidos sobre el total de pacientes del grupo.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Fallecidas entre embarazadas y no embarazadas"),
            output_widget("barras_embarazo"),
            ui.p("Solo se incluyen mujeres, porque en los hombres la variable no aplica. Hay apenas 8 embarazadas en la muestra, así que este resultado no permite concluir si el embarazo se asocia con el fallecimiento",
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