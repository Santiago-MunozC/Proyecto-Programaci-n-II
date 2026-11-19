import pandas as pd
from shiny import module, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go
from modulos.datos import COMORBILIDADES, ETIQUETAS_EDAD

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
    "N_COMORB_CAT": "Número de comorbilidades",
}
CATEGORIAS = {
    "GRUPO_EDAD": ETIQUETAS_EDAD,
    "TIPO_PACIENTE": ["Ambulatorio", "Hospitalizado"],
    "SEXO": ["Hombre", "Mujer"],
    "PRUEBA": ["Positivo", "No positivo"],
    "N_COMORB_CAT": ["0", "1", "2", "3 o más"],
}

COLORES = {
    "GRUPO_EDAD": PALETA[:len(ETIQUETAS_EDAD)],
    "TIPO_PACIENTE": [AZUL, ROJO],
    "SEXO": [AZUL, ROJO],
    "PRUEBA": [ROJO, AZUL],
    "N_COMORB_CAT": PALETA[:4],
}

INDICADORES = {
    "edad": "Edad mediana (años)",
    "hombres": "% de hombres",
    "comorb": "% con al menos una comorbilidad",
    "hosp": "% hospitalizados",
    "positivo": "% con prueba positiva",
}


def _etiqueta_mes(f):
    return f"{MESES[f.month]} {f.year}"

def _fecha_corta(f):
    return f"{f.day} {MESES[f.month]} {f.year}"

def _valor(sub, clave):
    """Valor de un indicador para un grupo de fallecidos (None si el grupo está vacío)."""
    if len(sub) == 0:
        return None
    if clave == "edad":
        return float(sub["AGE"].median())
    if clave == "hombres":
        return float((sub["SEXO"] == "Hombre").mean() * 100)
    if clave == "comorb":
        return float((sub["N_COMORB"] > 0).mean() * 100)
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

def _tabla_burbujas(df, meses):
    """Una fila por mes y comorbilidad, con los fallecidos acumulados hasta ese mes."""
    filas = []
    for m in meses:
        acum = df[df["MES"] <= m]
        n_total = len(acum)
        for columna, nombre in COMORBILIDADES.items():
            sub = acum[acum[columna] == 1]
            n = len(sub)
            filas.append({
                "MES": m, "comorbilidad": nombre, "n": n, "n_total": n_total,
                "pct": n / n_total * 100 if n else None,
                "edad": float(sub["AGE"].median()) if n else None,
            })
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


def _fig_burbujas(df, meses):
    tabla = _tabla_burbujas(df, meses)
    if tabla["n"].max() == 0:
        return _figura_vacia("Ningún fallecido con comorbilidades con los filtros elegidos")

    nombres = list(COMORBILIDADES.values())
    max_n = int(tabla["n"].max())
    sizeref = 2 * max_n / (60 ** 2)
    x_max = float(tabla["pct"].max()) * 1.2 + 5
    y_min = max(0.0, float(tabla["edad"].min()) - 10)
    y_max = float(tabla["edad"].max()) + 10

    def trazo(mes):
        sub = tabla[tabla["MES"] == mes].set_index("comorbilidad").reindex(nombres)
        return go.Scatter(
            x=sub["pct"], y=sub["edad"], mode="markers+text",
            text=[nombre if n > 0 else "" for nombre, n in zip(nombres, sub["n"])],
            textposition="top center",
            marker=dict(size=sub["n"], sizemode="area", sizeref=sizeref,
                        color=PALETA, line=dict(width=1, color="white")),
            customdata=list(zip(sub["n"], sub["n_total"])),
            hovertemplate="<b>%{text}</b><br>%{customdata[0]} de %{customdata[1]} fallecidos"
                          "<br>%{x:.1f}% de los fallecidos<br>Edad mediana: %{y:.0f} años<extra></extra>",
        )

    etiquetas = [_etiqueta_mes(m) for m in meses]
    frames = [go.Frame(name=etq, data=[trazo(m)]) for m, etq in zip(meses, etiquetas)]
    fig = go.Figure(data=[trazo(meses[0])], frames=frames)

    fig.add_annotation(
        xref="paper", yref="paper", x=1, y=1.08, xanchor="right", showarrow=False,
        text="Tamaño de la burbuja = número de fallecidos con esa comorbilidad",
        font=dict(size=11, color="gray"),
    )
    fig.update_layout(
        xaxis=dict(title="% de los fallecidos (acumulados) que tienen la comorbilidad",
                   range=[0, x_max]),
        yaxis=dict(title="Edad mediana de esos fallecidos (años)", range=[y_min, y_max]),
        showlegend=False,
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.1, y=0, xanchor="right", yanchor="top",
            pad=dict(r=10, t=87),
            buttons=[
                dict(label="▶ Reproducir", method="animate",
                     args=[None, {"frame": {"duration": 1300, "redraw": True},
                                  "fromcurrent": True,
                                  "transition": {"duration": 500}}]),
                dict(label="⏸ Pausar", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}]),
            ],
        )],
        sliders=[dict(
            active=0, x=0.1, len=0.9, pad=dict(t=87),
            currentvalue=dict(prefix="Fallecidos acumulados hasta: "),
            steps=[dict(label=etq, method="animate",
                        args=[[etq], {"mode": "immediate",
                                      "frame": {"duration": 0, "redraw": True},
                                      "transition": {"duration": 0}}])
                   for etq in etiquetas],
        )],
    )
    return fig
