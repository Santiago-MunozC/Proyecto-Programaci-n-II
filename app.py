from shiny import App, ui, render
import plotly.express as px

tips = px.data.tips()

app_ui = ui.page_fluid(
    ui.h2("Tablero de propinas"),
    ui.input_slider("min_cuenta", "Monto mínimo de la cuenta (USD)",
                    min=0, max=51, value=0),
    ui.output_text("resumen"),
)


def server(input, output, session):
    @render.text
    def resumen():
        datos = tips[tips["total_bill"] >= input.min_cuenta()]
        return f"Mesas que cumplen el filtro: {len(datos)} de {len(tips)}"


app = App(app_ui, server)
