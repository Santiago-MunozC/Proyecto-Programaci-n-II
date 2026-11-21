import pandas as pd
from shiny import module, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from modulos.datos import ETIQUETAS_EDAD

AZUL = "#636EFA"
ROJO = "#EF553B"
PALETA = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
          "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
COLOR_BARRAS = ROJO
COLOR_ACUM = AZUL
COLOR_LINEA = AZUL
COLOR_POCOS = "#B0B0B0"
MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


APILAR = {
    "GRUPO_EDAD": "Grupo de edad",
    "TIPO_PACIENTE": "Tipo de paciente",
    "SEXO": "Sexo",
    "PRUEBA": "Resultado de la prueba",
}
CATEGORIAS = {
    "GRUPO_EDAD": ETIQUETAS_EDAD,
    "TIPO_PACIENTE": ["Ambulatorio", "Hospitalizado"],
    "SEXO": ["Hombre", "Mujer"],
    "PRUEBA": ["Positivo", "No positivo"],
}

COLORES = {
    "GRUPO_EDAD": PALETA[:len(ETIQUETAS_EDAD)],
    "TIPO_PACIENTE": [AZUL, ROJO],
    "SEXO": [AZUL, ROJO],
    "PRUEBA": [ROJO, AZUL],
}

INDICADORES = {
    "edad": "Edad mediana (años)",
    "hombres": "% de hombres",
    "hosp": "% hospitalizados",
    "positivo": "% con prueba positiva",
}


def _etiqueta_mes(f):
    return f"{MESES[f.month]} {f.year}"

def _valor(sub, clave):
    """Valor de un indicador para un grupo de fallecidos (None si el grupo está vacío)."""
    if len(sub) == 0:
        return None
    if clave == "edad":
        return float(sub["AGE"].median())
    if clave == "hombres":
        return float((sub["SEXO"] == "Hombre").mean() * 100)
    if clave == "hosp":
        return float((sub["TIPO_PACIENTE"] == "Hospitalizado").mean() * 100)
    return float((sub["PRUEBA"] == "Positivo").mean() * 100)  # positivo

def _indicador_por_mes(df, meses, clave):
    """Para cada mes devuelve cuántos fallecidos hay (n) y el valor del indicador."""
    filas = []
    for m in meses:
        sub = df[df["MES"] == m]
        filas.append({"MES": m, "n": len(sub), "valor": _valor(sub, clave)})
    return pd.DataFrame(filas)

def _tabla_apilada(df, meses, variable):
    categorias = CATEGORIAS[variable]
    return (
        df.groupby(["MES", variable], observed=False)
        .size()
        .unstack(fill_value=0)
        .reindex(index=meses, columns=categorias, fill_value=0)
    )

def _figura_vacia(mensaje="No hay fallecimientos con los filtros elegidos"):
    fig = go.Figure()
    fig.add_annotation(text=mensaje, showarrow=False, font=dict(size=16))
    fig.update_layout(xaxis_visible=False, yaxis_visible=False)
    return fig

def _fig_serie(df, periodo):
    if periodo == "semana":
        inicio = df["FECHA"].dt.to_period("W").dt.start_time
        conteo = inicio.value_counts().sort_index()
        rango = pd.date_range(conteo.index.min(), conteo.index.max(), freq="7D")
        etiqueta_hover = "Semana del %{x|%d %b}"
    else:
        conteo = df["MES"].value_counts().sort_index()
        rango = pd.date_range(conteo.index.min(), conteo.index.max(), freq="MS")
        etiqueta_hover = "%{x|%b %Y}"
    # Se rellenan con 0 los periodos sin fallecimientos
    conteo = conteo.reindex(rango, fill_value=0)
    acumulado = conteo.cumsum()

    fig = go.Figure()
    fig.add_bar(
        x=conteo.index, y=conteo.values, name="Fallecimientos",
        marker_color=COLOR_BARRAS,
        hovertemplate=etiqueta_hover + ": %{y} fallecidos<extra></extra>",
    )
    fig.add_scatter(
        x=acumulado.index, y=acumulado.values, name="Acumulado",
        mode="lines+markers", line=dict(color=COLOR_ACUM), yaxis="y2",
        hovertemplate="Acumulado: %{y}<extra></extra>",
    )
    fig.add_annotation(
        x=conteo.idxmax(), y=int(conteo.max()), text=f"Máximo: {int(conteo.max())}",
        showarrow=True, arrowhead=2, ax=0, ay=-35, font=dict(size=12),
    )
    fig.update_layout(
        xaxis_title="Fecha (2020)",
        yaxis=dict(title="Fallecimientos por " + periodo, rangemode="tozero"),
        yaxis2=dict(title="Total acumulado", overlaying="y", side="right",
                    rangemode="tozero", showgrid=False),
        legend=dict(orientation="h", y=1.1),
    )
    return fig

def _fig_apiladas(df, meses, variable, como):
    tabla = _tabla_apilada(df, meses, variable)
    totales = tabla.sum(axis=1)
    if como == "porcentaje":
        valores = tabla.div(totales.where(totales > 0), axis=0).fillna(0) * 100
        titulo_y = "% de los fallecidos del mes"
        plantilla = "%{x|%b %Y}, %{fullData.name}: %{y:.1f}% (n = %{customdata})<extra></extra>"
    else:
        valores = tabla
        titulo_y = "Número de fallecidos"
        plantilla = "%{x|%b %Y}, %{fullData.name}: %{y}<extra></extra>"

    fig = go.Figure()
    for categoria, color in zip(CATEGORIAS[variable], COLORES[variable]):
        fig.add_bar(
            x=valores.index, y=valores[categoria], name=categoria,
            marker_color=color,
            customdata=tabla[categoria], hovertemplate=plantilla,
        )
    # Nota sobre cada barra: cuántos fallecidos hay en ese mes
    tope = 100 if como == "porcentaje" else int(totales.max())
    for mes, total in totales.items():
        if total > 0:
            fig.add_annotation(
                x=mes, y=100 if como == "porcentaje" else int(total),
                text=f"n = {int(total)}", showarrow=False, yshift=12,
                font=dict(size=11),
            )
    fig.update_layout(
        barmode="stack",
        xaxis_title="Mes de fallecimiento (2020)",
        yaxis_title=titulo_y,
        yaxis_range=[0, tope * 1.15],
        legend_title=APILAR[variable],
    )
    return fig


def _fig_perfil(df, meses, clave):
    datos_mes = _indicador_por_mes(df, meses, clave)
    es_porcentaje = clave != "edad"
    # Tamaño del punto proporcional al número de fallecidos del mes
    tamanos = [8 + 3 * (n ** 0.5) if n else 0 for n in datos_mes["n"]]
    # Los meses con menos de 5 fallecidos se pintan en gris: son poco confiables
    colores = [COLOR_LINEA if n >= 5 else COLOR_POCOS for n in datos_mes["n"]]
    fig = go.Figure(
        go.Scatter(
            x=datos_mes["MES"], y=datos_mes["valor"],
            mode="lines+markers", connectgaps=False,
            line=dict(color=COLOR_LINEA),
            marker=dict(size=tamanos, color=colores),
            customdata=datos_mes["n"],
            hovertemplate="%{x|%b %Y}: %{y:.1f}<br>n = %{customdata} fallecidos<extra></extra>",
        )
    )
    total = _valor(df, clave)
    if total is not None:
        fig.add_hline(
            y=total, line_dash="dash", line_color="gray",
            annotation_text=f"Todos los meses: {total:.1f}",
            annotation_position="top left",
        )
    fig.add_annotation(
        xref="paper", yref="paper", x=1, y=1.12, xanchor="right", showarrow=False,
        text="Gris: mes con menos de 5 fallecidos (poco confiable)",
        font=dict(size=11, color="gray"),
    )
    fig.update_layout(
        xaxis_title="Mes de fallecimiento (2020)",
        yaxis_title=INDICADORES[clave],
        yaxis_range=[0, 105] if es_porcentaje else [0, 100],
        showlegend=False,
    )
    return fig


@module.ui
def evolucion_temporal_ui():
    return ui.div(
        ui.h4("4. Evolución temporal"),
        ui.p("¿Cómo se distribuyeron los fallecimientos y qué perfil tenían en cada mes?"),
        ui.div(
            ui.tags.strong("Contexto de los datos: "),
            "el conjunto de datos solo trae la fecha de fallecimiento (DATE_DIED); no incluye fecha de inicio de síntomas, de ingreso ni de la prueba. Por eso esta pestaña muestra cuándo murieron los pacientes de la muestra, no una curva de contagios. Además, solo 69 de los 1,000 pacientes fallecieron: hay meses con 1 o 4 fallecidos y, si se aplican filtros, los grupos se vuelven aún más pequeños. Sirve para ver el patrón general, no para estimar la evolución real de la epidemia en México.",
            class_="alert alert-info",
        ),
        ui.card(
            ui.card_header("Filtros"),
            ui.layout_columns(
                ui.input_select("sexo", "Sexo", ["Todos", "Mujer", "Hombre"]),
                ui.input_select(
                    "tipo", "Tipo de paciente",
                    ["Todos", "Ambulatorio", "Hospitalizado"],
                ),
                ui.input_select(
                    "prueba", "Resultado de la prueba",
                    ["Todos", "Positivo", "No positivo"],
                ),
            ),
            ui.input_checkbox_group(
                "edades", "Grupo de edad",
                ETIQUETAS_EDAD, selected=ETIQUETAS_EDAD, inline=True,
            ),
            ui.p(
                "Los filtros actualizan las tarjetas y los gráficos. Los comentarios en gris describen la muestra completa.",
                class_="text-muted",
            ),
        ),
        ui.layout_columns(
            ui.value_box("Fallecidos", ui.output_text("n_fall")),
            ui.value_box("Mes con más fallecimientos", ui.output_text("mes_pico")),
            ui.value_box("Edad mediana", ui.output_text("edad_mediana")),
            ui.value_box("Hospitalizados", ui.output_text("n_hosp")),
            fill=False,
        ),
        ui.card(
            ui.card_header("Fallecimientos en el tiempo y total acumulado"),
            ui.input_radio_buttons(
                "periodo", "Agrupar por",
                {"mes": "Mes", "semana": "Semana"}, inline=True,
            ),
            ui.p(
                ui.tags.strong("Cómo leerlo: "),
                "las barras rojas son los fallecimientos de cada periodo; la línea azul suma todos los anteriores. La flecha marca el periodo con más fallecimientos.",
                class_="text-muted",
            ),
            output_widget("serie"),
            ui.p(
                "Los 69 fallecimientos de la muestra ocurren entre el 26 de marzo y el 3 de septiembre de 2020, pero casi todos se concentran en tres meses: 20 en mayo, 22 en junio y 20 en julio (62 de 69, el 89.9%). Antes hay solo 5 (1 en marzo y 4 en abril) y después solo 2 (1 en agosto y 1 en septiembre). Al agrupar por semana el patrón es irregular; la semana con más fallecimientos es la del 8 de junio, con 11.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("Perfil de los fallecidos en cada mes (barras apiladas)"),
            ui.layout_columns(
                ui.input_select("apilar", "Dividir cada barra según", APILAR),
                ui.input_radio_buttons(
                    "como", "Mostrar",
                    {"numero": "Número de fallecidos", "porcentaje": "Porcentaje del mes"},
                    inline=True,
                ),
            ),
            ui.p(
                ui.tags.strong("Cómo leerlo: "),
                "cada barra es un mes y sus colores muestran cómo se reparten los fallecidos de ese mes. El n sobre la barra es el total de fallecidos del mes: en Porcentaje, cada barra suma 100% sin importar cuántos casos tenga.",
                class_="text-muted",
            ),
            output_widget("apiladas"),
            ui.p(
                "Casi todos los fallecidos estaban hospitalizados (65 de 69, el 94.2%); solo 4 fueron ambulatorios (1 en junio, 2 en julio y 1 en septiembre). Junio es el mes con más hombres (17 de 22, el 77.3%), mientras que en mayo y julio son 12 de 20 (60%). Entre los fallecidos de julio, 17 de 20 (85%) dieron positivo, frente a 50% en mayo y 54.5% en junio; la categoría No positivo incluye resultados negativos y no concluyentes. En el porcentaje, marzo, agosto y septiembre (1 fallecido cada uno) dan barras de 0% o 100% que no significan nada.",
                class_="text-muted",
            ),
        ),
        ui.card(
            ui.card_header("¿Cambió el perfil de un mes a otro? (puntos con líneas)"),
            ui.input_select("indicador", "Indicador", INDICADORES),
            ui.p(
                ui.tags.strong("Cómo leerlo: "),
                "cada punto resume a los fallecidos de un mes con el indicador elegido. La línea punteada es el valor de todos los meses juntos, para comparar si un mes está por encima o por debajo. Los puntos grises tienen menos de 5 fallecidos.",
                class_="text-muted",
            ),
            output_widget("perfil"),
            ui.p(
                 "El tamaño de cada punto es proporcional al número de fallecidos del mes. En los tres meses con más casos el perfil es parecido: la edad mediana es de 63 años en mayo, 58.5 en junio y 65 en julio, y el porcentaje de hombres es de 60%, 77.3% y 60%. Lo que más cambia es el porcentaje con prueba positiva: 50% en mayo, 54.5% en junio y 85% en julio (65.2% en todos los meses); la categoría No positivo incluye resultados negativos y no concluyentes. Los puntos de marzo, agosto y septiembre (1 fallecido) y abril (4) no permiten comparar.",
                 class_="text-muted",
            ),
        ),
    )


@module.server
def evolucion_temporal_server(input, output, session, datos):

    # Solo los fallecidos tienen fecha; en el resto DATE_DIED es "9999-99-99"
    base = datos.copy()
    base["FECHA"] = pd.to_datetime(
        base["DATE_DIED"].where(base["FALLECIDO"] == 1), errors="coerce"
    )
    base["MES"] = base["FECHA"].dt.to_period("M").dt.start_time
    fallecidos = base[base["FECHA"].notna()].copy()

    # Los meses del eje son siempre los de toda la muestra, aunque haya filtros
    meses = pd.date_range(fallecidos["MES"].min(), fallecidos["MES"].max(), freq="MS")

    @reactive.calc
    def fall_filtrados():
        df = fallecidos
        if input.sexo() != "Todos":
            df = df[df["SEXO"] == input.sexo()]
        if input.tipo() != "Todos":
            df = df[df["TIPO_PACIENTE"] == input.tipo()]
        if input.prueba() != "Todos":
            df = df[df["PRUEBA"] == input.prueba()]
        df = df[df["GRUPO_EDAD"].isin(list(input.edades()))]
        return df

    @render.text
    def n_fall():
        return f"{len(fall_filtrados()):,}"

    @render.text
    def mes_pico():
        df = fall_filtrados()
        if len(df) == 0:
            return "—"
        conteo = df["MES"].value_counts().sort_index()
        mes = conteo.idxmax()
        return f"{_etiqueta_mes(mes)} ({conteo.max()})"

    @render.text
    def edad_mediana():
        df = fall_filtrados()
        return f"{df['AGE'].median():.0f} años" if len(df) else "—"

    @render.text
    def n_hosp():
        df = fall_filtrados()
        if len(df) == 0:
            return "—"
        n = int((df["TIPO_PACIENTE"] == "Hospitalizado").sum())
        return f"{n:,} ({n / len(df):.1%})"

    @render_widget
    def serie():
        df = fall_filtrados()
        if len(df) == 0:
            return _figura_vacia()
        return _fig_serie(df, input.periodo())

    @render_widget
    def apiladas():
        df = fall_filtrados()
        if len(df) == 0:
            return _figura_vacia()
        return _fig_apiladas(df, meses, input.apilar(), input.como())

    @render_widget
    def perfil():
        df = fall_filtrados()
        if len(df) == 0:
            return _figura_vacia()
        return _fig_perfil(df, meses, input.indicador())

    
