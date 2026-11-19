# modulos/tab_edad.py
import plotly.express as px
from shiny import module, render, ui
from shinywidgets import output_widget, render_widget


# UI 
@module.ui   
def edad_ui():
    return ui.div(
        ui.h4("Edad y comorbilidades"),
        ui.p(
            "¿Cómo cambia la proporción de fallecidos según la edad "
            "y qué comorbilidades se asocian con ella?",
            class_="text-muted",   # texto gris, igual que en tab_atencion
        ),
        ui.card(                                    # una tarjeta por gráfico
            ui.card_header("Edad de fallecidos y sobrevivientes"),
            output_widget("boxplot_edad"),       
            ui.p(
                "La caja muestra donde se concentra la mitad central de las "
                "edades; la línea dentro de la caja es la mediana.",
                class_="text-muted",
            ),
        ),
    )


# SERVER
@module.server
def edad_server(input, output, session, datos):

    @render_widget            # sin @output; el nombre de la función = id del output_widget
    def boxplot_edad():
        df = datos.copy()     # copia para no modificar la base original
        # FALLECIDO es 0/1 a texto 
        df["DESENLACE"] = df["FALLECIDO"].map({1: "Fallecido", 0: "Sobreviviente"})

        fig = px.box(
            df,
            x="DESENLACE",
            y="AGE",
            color="DESENLACE",                      
            category_orders={"DESENLACE": ["Sobreviviente", "Fallecido"]},
            labels={"AGE": "Edad (años)", "DESENLACE": "Desenlace"},
        )
        fig.update_layout(showlegend=False)          
        return fig