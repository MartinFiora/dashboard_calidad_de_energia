# Carga de librerías

import pandas as pd
import janitor
import plotly.graph_objects as go
from pathlib import Path

# Carga y parseo de datos ----

datos_fluke = (
    pd.read_csv(
        filepath_or_buffer = "./data/original_fluke.csv",
        encoding = "latin1",
        sep = ";",
        decimal = ",",
        parse_dates = ["date"],
        date_format = "%d.%m.%Y %H:%M:%S"
     )
    .clean_names(strip_underscores=True)
)

# Función para graficar conjuntos de variables

def plot_bandas_trifasico(
    df: pd.DataFrame,
    fases: list[dict], 
    prefijo: str | None = "",
    lim_inf: float | None = None,
    lim_sup: float | None = None,
    col_fecha: str = "date",
) -> go.Figure:

    fig = go.Figure()

    for f in fases:
        col_max = f"{prefijo}{f['id']}_max"
        col_min = f"{prefijo}{f['id']}_min"
        col_med = f"{prefijo}{f['id']}_med"
        grupo = f["nombre"]

        # 1. Límite superior de la banda
        fig.add_trace(go.Scatter(
            x=df[col_fecha],
            y=df[col_max],
            mode="lines",
            line={"width": 0},
            legendgroup=grupo,
            showlegend=False,
            name=f"{grupo} Max"
        ))

        # 2. Límite inferior + banda sombreada
        fig.add_trace(go.Scatter(
            x=df[col_fecha],
            y=df[col_min],
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor=f["fill"],
            legendgroup=grupo,
            showlegend=False,
            name=f"{grupo} Min"
        ))

        # 3. Línea de valor medio
        fig.add_trace(go.Scatter(
            x=df[col_fecha],
            y=df[col_med],
            mode="lines",
            name=f"{grupo} Media",
            legendgroup=grupo,
            line={"color": f["color"], "width": 1.8}
        ))

        # 4. Outliers inferiores

        if lim_inf is not None:
            df_outlier = df[df[col_min] < lim_inf]
            if not df_outlier.empty:
                        fig.add_trace(go.Scatter(
                            x=df_outlier[col_fecha],
                            y=df_outlier[col_min],
                            mode="markers",
                            marker={
                                "color": f["color"],
                                "size": 10,
                                "symbol": "triangle-down",
                            },
                            legendgroup=grupo,
                            showlegend=False,
                            name=f"Evento en {grupo}"
        ))

        # 5. Outliers superiores

        if lim_sup is not None:
            df_outlier = df[df[col_max] > lim_sup]
            if not df_outlier.empty:
                        fig.add_trace(go.Scatter(
                            x=df_outlier[col_fecha],
                            y=df_outlier[col_max],
                            mode="markers",
                            marker={
                                "color": f["color"],
                                "size": 10,
                                "symbol": "triangle-up",
                            },
                            legendgroup=grupo,
                            showlegend=False,
                            name=f"Evento en {grupo}"
        ))

    if lim_inf:
        fig.add_hline(
            y=lim_inf,
            line_dash="dash",
            line_color="crimson",
            line_width=1.5
                )

    if lim_sup:
        fig.add_hline(
            y=lim_sup,
            line_dash="dash",
            line_color="crimson",
            line_width=1.5
                )

    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        legend={"orientation": "h", "y": 1.05, "x": 0},
        dragmode='pan'
    )

    fig.update_xaxes(tickformat = "%d/%m %H:%M")

    return fig

# Exploración de tensiones ----

# Configuración de fases

fases_ln = [
    {"id": "l1n", "nombre": "L1", "color": "#d62728", "fill": "rgba(214, 39, 40, 0.18)"},
    {"id": "l2n", "nombre": "L2", "color": "#1f77b4", "fill": "rgba(31, 119, 180, 0.18)"},
    {"id": "l3n", "nombre": "L3", "color": "#2ca02c", "fill": "rgba(44, 160, 44, 0.18)"},
    {"id": "ng",  "nombre": "NG", "color": "#9467bd", "fill": "rgba(148, 103, 189, 0.18)"},
]

fig_tension_linea = plot_bandas_trifasico(
    df = datos_fluke,
    fases = fases_ln[0:3],
    prefijo="tension_",
    lim_inf = 198,
    lim_sup = 242
    )

fig_tension_linea.update_layout(
    title = "Evolución temporal de la tensión por fase",
    xaxis_title = "Fecha y hora",
    yaxis_title = "Tensión (V)",
    yaxis = {"hoverformat": ".2f", "ticksuffix": " V"},
)

fig_tension_neutro = plot_bandas_trifasico(
    df = datos_fluke,
    fases = fases_ln[3:],
    prefijo="tension_",
    lim_sup = 4.4)

fig_tension_neutro.update_layout(
    title = "Evolución temporal de la tensión de neutro",
    xaxis_title = "Fecha y hora",
    yaxis_title = "Tensión (V)",
    yaxis = {"hoverformat": ".2f", "ticksuffix": " V"},
)

# Exploración de corrientes ----

# Configuración de fases

fases_l = [
    {"id": "l1", "nombre": "L1", "color": "#d62728", "fill": "rgba(214, 39, 40, 0.18)"},
    {"id": "l2", "nombre": "L2", "color": "#1f77b4", "fill": "rgba(31, 119, 180, 0.18)"},
    {"id": "l3", "nombre": "L3", "color": "#2ca02c", "fill": "rgba(44, 160, 44, 0.18)"},
    {"id": "n",  "nombre": "N", "color": "#9467bd", "fill": "rgba(148, 103, 189, 0.18)"},
]

fig_corriente_linea = plot_bandas_trifasico(
    df = datos_fluke,
    fases = fases_l[0:3],
    prefijo="corriente_")

fig_corriente_linea.update_layout(
    title = "Evolución temporal de la corriente por fase",
    xaxis_title = "Fecha y hora",
    yaxis_title = "Corriente (A)",
    yaxis = {"hoverformat": ".2f", "ticksuffix": " A"},
)

fig_corriente_neutro = plot_bandas_trifasico(
    df = datos_fluke,
    fases = fases_l[3:],
    prefijo="corriente_")

fig_corriente_neutro.update_layout(
    title = "Evolución temporal de la corriente de neutro",
    xaxis_title = "Fecha y hora",
    yaxis_title = "Corriente (A)",
    yaxis = {"hoverformat": ".2f", "ticksuffix": " A"},
)

# Exploración de frecuencia ----

freq = [
    {"id": "frecuencia",  "nombre": "Frecuencia", "color": "#9467bd", "fill": "rgba(148, 103, 189, 0.18)"},
]

fig_freq = plot_bandas_trifasico(
    df = datos_fluke,
    fases = freq,
    lim_inf= 49.5,
    lim_sup = 50.5)

fig_freq.update_layout(
    title = "Evolución temporal de la corriente de la frecuencia",
    xaxis_title = "Fecha y hora",
    yaxis_title = "Frecuencia (Hz)",
    yaxis = {"hoverformat": ".2f", "ticksuffix": " Hz"},
)

# Exportación de gráficos

graficos = {
    "Tensiones de linea": fig_tension_linea,
    "Tension de neutro": fig_tension_neutro,
    "Corrientes de linea": fig_corriente_linea,
    "Corriente de neutro": fig_corriente_neutro,
    "Frecuencia": fig_freq,
}

Path("./output").mkdir(exist_ok = True)

for nombre, fig in graficos.items():
    fig.write_html(
        file = f"output/{nombre}.html",
        config = {"scrollZoom": True},
        auto_open = False,
        full_html = True,
        include_plotlyjs = 'cdn'
    )

    
