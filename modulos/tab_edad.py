# modulos/tab_edad.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import module, reactive, ui
from shinywidgets import output_widget, render_widget

from modulos.datos import COMORBILIDADES, ETIQUETAS_EDAD


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
        ui.card(
            ui.card_header("% de fallecidos con y sin cada comorbilidad"),
            output_widget("barras_comorbilidad"),
            ui.p(
                "Las comorbilidades están ordenadas por la diferencia en puntos "
                "porcentuales entre quienes la tienen y quienes no. Cada barra "
                "muestra el porcentaje y, entre paréntesis, los fallecidos sobre "
                "el total del grupo. Las comorbilidades poco frecuentes dan "
                "porcentajes poco estables.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("% de fallecidos según el número de comorbilidades"),
            output_widget("barras_n_comorbilidades"),
            ui.p(
                "Se cuentan las 10 comorbilidades de cada paciente (incluyendo "
                "tabaquismo y otra enfermedad). Cada barra muestra el porcentaje "
                "de fallecidos y, entre paréntesis, los fallecidos sobre el total "
                "de pacientes del grupo. Los grupos con pocos pacientes dan "
                "porcentajes poco estables.",
                class_="text-muted",
            ),
        ), 
        ui.card(
            ui.card_header("Mapa de calor: % de fallecidos por comorbilidad y grupo de edad"),
            ui.input_slider(
                "min_n", "Mínimo de pacientes por celda",
                min=1, max=30, value=10,
            ),
            output_widget("mapa_calor"),
            ui.p(
                "Cada celda muestra el porcentaje de fallecidos entre los pacientes "
                "que tienen esa comorbilidad y están en ese grupo de edad, y entre "
                "paréntesis los fallecidos sobre el total de la celda. Las celdas "
                "grises tienen menos pacientes que el mínimo elegido y sus "
                "porcentajes no son confiables.",
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

    # Gráfico 3 (prescencia de comorbilidades)
    @render_widget
    def barras_comorbilidad():
        df = datos_filtrados()

        # Tabla larga, una fila por cmorbilidad, con y sin
        filas = []
        for col, nombre in COMORBILIDADES.items():      
            for valor, grupo in [(1, "Con"), (2, "Sin")]: 
                sub = df[df[col] == valor]              
                filas.append({
                    "Comorbilidad": nombre,
                    "Grupo": grupo,
                    "fallecidos": int(sub["FALLECIDO"].sum()),
                    "total": len(sub),
                })
        tabla = pd.DataFrame(filas)

        # Porcentaje cuidando la división entre 0
        tabla["porcentaje"] = (
            tabla["fallecidos"] / tabla["total"].where(tabla["total"] > 0) * 100
        ).fillna(0)
        tabla["texto"] = tabla.apply(
            lambda f: f"{f['porcentaje']:.1f}% ({f['fallecidos']} de {f['total']})",
            axis=1,
        )

        # Diferencia en puntos porcentuales (Con - Sin).
        # pivot pone "Con" y "Sin" en columnas para poder restarlas.
        ancho = tabla.pivot(index="Comorbilidad", columns="Grupo", values="porcentaje")
        orden = (ancho["Con"] - ancho["Sin"]).sort_values(ascending=False).index.tolist()
        # sort_values() va de menor a mayor y plotly dibuja la primera categoría abajo, por lo que la mayor diferencia queda arriba

        # Barras agrupadas
        fig = px.bar(
            tabla,
            y="Comorbilidad", x="porcentaje", color="Grupo",
            orientation="h", barmode="group", text="texto",
            category_orders={"Comorbilidad": orden, "Grupo": ["Sin", "Con"]},
            color_discrete_map={"Con": "#EF553B", "Sin": "#636EFA"},
            labels={"porcentaje": "% de fallecidos", "Comorbilidad": ""},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, max(tabla["porcentaje"].max() * 1.5, 5)])
        fig.update_layout(height=650, legend_title_text="Comorbilidad")
        return fig

    # Gráfico 4 (fallecidos según número de comorbilidades)
    @render_widget
    def barras_n_comorbilidades():
        ORDEN = ["0", "1", "2", "3 o más"]
        df = datos_filtrados().copy()

        # Comorbilidades por paciente.
        # True cuenta como 1
        # .clip(upper=3) = todo lo que sea 3 o más se queda en 3
        n = (df[list(COMORBILIDADES)] == 1).sum(axis=1).clip(upper=3)

        # Etiquetas ordenadas
        df["N_COMORB"] = pd.Categorical(
            n.map({0: "0", 1: "1", 2: "2", 3: "3 o más"}),
            categories=ORDEN, ordered=True,
        )

        # fallecidos y total por grupo
        tabla = (
            df.groupby("N_COMORB", observed=False)["FALLECIDO"]
            .agg(fallecidos="sum", total="count")
            .reset_index()
        )
        tabla["porcentaje"] = (
            tabla["fallecidos"] / tabla["total"].where(tabla["total"] > 0) * 100
        ).fillna(0)
        tabla["texto"] = tabla.apply(
            lambda f: f"{f['porcentaje']:.1f}% ({int(f['fallecidos'])} de {int(f['total'])})",
            axis=1,
        )

        # Barras
        fig = px.bar(
            tabla, x="N_COMORB", y="porcentaje", text="texto",
            category_orders={"N_COMORB": ORDEN},
            color_discrete_sequence=["#EF553B"],
            labels={"porcentaje": "% de fallecidos",
                    "N_COMORB": "Número de comorbilidades"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, max(tabla["porcentaje"].max() * 1.3, 5)])
        return fig
    
    # Gráfico 5 (mapa de calor comorbilidad x grupo de edad)
    @render_widget
    def mapa_calor():
        df = datos_filtrados()
        minimo = input.min_n()          # slider

        # Tres matrices una fila por comorbilidad una columna por grupo de edad.
        z, texto, custom = [], [], []
        for col in COMORBILIDADES:
            fila_z, fila_t, fila_c = [], [], []
            for grupo in ETIQUETAS_EDAD:
                # Pacientes que TIENEN esa comorbilidad y están en ese grupo de edad
                sub = df[(df[col] == 1) & (df["GRUPO_EDAD"] == grupo)]
                n = len(sub)
                f = int(sub["FALLECIDO"].sum())
                if n >= minimo:
                    pct = f / n * 100
                    fila_z.append(pct)                         
                    fila_t.append(f"{pct:.0f}%<br>({f} de {n})") 
                else:
                    fila_z.append(None)    # celda vacía se verá gris
                    fila_t.append("")
                fila_c.append([f, n])      
            z.append(fila_z)
            texto.append(fila_t)
            custom.append(fila_c)

        fig = go.Figure(
            go.Heatmap(
                z=z,
                x=ETIQUETAS_EDAD,
                y=list(COMORBILIDADES.values()),
                text=texto,
                texttemplate="%{text}",     
                customdata=custom,
                hovertemplate=(
                    "%{y}<br>Edad: %{x}"
                    "<br>% de fallecidos: %{z:.1f}%"
                    "<br>%{customdata[0]} de %{customdata[1]} pacientes"
                    "<extra></extra>"
                ),
                colorscale="Reds",
                zmin=0,                       # 0% siempre es el color más claro
                colorbar={"title": "% fallecidos"},
                hoverongaps=False,
                xgap=2, ygap=2,              
            )
        )
        fig.update_yaxes(autorange="reversed")      # La primera comorbilidad arriba
        fig.update_xaxes(title="Grupo de edad")
        fig.update_layout(height=600, plot_bgcolor="#D9D9D9") 
        return fig