# modulos/tab_edad.py
import plotly.express as px
from shiny import module, reactive, ui
from shinywidgets import output_widget, render_widget

from modulos.datos import ETIQUETAS_EDAD


@module.ui
def edad_ui():
    return ui.div(
        ui.h4("Edad y comorbilidades"),
        ui.p(
            "¿Cómo cambia la proporción de fallecidos según la edad y qué "
            "comorbilidades se asocian con ella?",
            class_="text-muted",
        ),
        # Aviso de muestra pequeña 
        ui.div(
            ui.tags.strong("Ojo con los grupos pequeños: "),
            "en toda la muestra hay solo 69 fallecidos. Con tan pocos casos, "
            "un porcentaje puede cambiar mucho por una sola persona, por eso "
            "las barras muestran también el número de pacientes.",
            class_="alert alert-warning",
        ),
        # Filtros
        ui.card(
            ui.card_header("Filtros"),
            ui.layout_columns(
                ui.input_select("sexo", "Sexo", ["Todos", "Mujer", "Hombre"]),
                ui.input_select(
                    "tipo", "Tipo de paciente", ["Todos", "Ambulatorio", "Hospitalizado"]
                ),
            ),
        ),
        ui.card(
            ui.card_header("Edad de fallecidos y sobrevivientes"),
            output_widget("boxplot_edad"),
            ui.p(
                "La caja muestra dónde se concentra la mitad central de las "
                "edades; la línea dentro de la caja es la mediana.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("% de fallecidos por grupo de edad"),
            output_widget("barras_grupo_edad"),
            ui.p(
                "Cada barra muestra el porcentaje de fallecidos y, entre "
                "paréntesis, los fallecidos sobre el total de pacientes del grupo.",
                class_="text-muted",
            ),
        ),
    )


@module.server
def edad_server(input, output, session, datos):

    # reactive.calc = es una recta que se recalcula sola cuando cambia un filtro.
    # Todos los gráficos la llaman con datos_filtrados() en vez de usar datos.
    @reactive.calc
    def datos_filtrados():
        df = datos
        if input.sexo() != "Todos":
            df = df[df["SEXO"] == input.sexo()]
        if input.tipo() != "Todos":
            df = df[df["TIPO_PACIENTE"] == input.tipo()]
        return df

    # Gráfico 1 (boxplot)
    @render_widget
    def boxplot_edad():
        df = datos_filtrados().copy()
        df["DESENLACE"] = df["FALLECIDO"].map({1: "Fallecido", 0: "Sobreviviente"})
        fig = px.box(
            df, x="DESENLACE", y="AGE", color="DESENLACE",
            category_orders={"DESENLACE": ["Sobreviviente", "Fallecido"]},
            labels={"AGE": "Edad (años)", "DESENLACE": "Desenlace"},
        )
        fig.update_layout(showlegend=False)
        return fig

    # Gráfico 2 (barras por edad)
    @render_widget
    def barras_grupo_edad():
        # Agrupar por grupo de edad
        tabla = (
            datos_filtrados()
            .groupby("GRUPO_EDAD", observed=False)["FALLECIDO"]
            .agg(fallecidos="sum", total="count")
            .reset_index()
        )
        # Porcentaje cuidando la división entre 0
        tabla["porcentaje"] = (
            tabla["fallecidos"] / tabla["total"].where(tabla["total"] > 0) * 100
        ).fillna(0)

        tabla["texto"] = tabla.apply(
            lambda f: f"{f['porcentaje']:.1f}% ({int(f['fallecidos'])} de {int(f['total'])})",
            axis=1,
        )
        
        fig = px.bar(
            tabla, x="GRUPO_EDAD", y="porcentaje", text="texto",
            category_orders={"GRUPO_EDAD": ETIQUETAS_EDAD},  
            labels={"porcentaje": "% de fallecidos", "GRUPO_EDAD": "Grupo de edad"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, max(tabla["porcentaje"].max() * 1.3, 5)])
        return fig