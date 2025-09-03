import plotly.graph_objects as pg
import pandas as pd
from datetime import datetime
from typing import Literal

from cashd import db


CORES = ["#478eff", "gray"]


def _preprocessar_data(
    tbl: pd.DataFrame,
    periodo: Literal["mes", "sem", "dia"],
    date_col: str = "Data",
) -> pd.DataFrame:
    """
    Retorna `tbl` com a coluna de data `date_col` formatada corretamente
    de acordo com a periodicidade em `periodo`
    """
    if periodo == "sem":
        tbl[date_col] = tbl[date_col].apply(
            lambda x: datetime.strptime(x + "-0", "%Y-%W-%w")
        )
    tbl[date_col] = pd.to_datetime(tbl.Data)
    return tbl


def _gerar_layout(
    tbl: pd.DataFrame, periodo: Literal["mes", "sem", "dia"], date_col: str = "Data"
) -> pg.Layout:
    """
    Retorna um `plotly.graph_objects.Layout` gerado para o conjunto de dados `tbl`
    """
    datestr = "%B de %Y"
    if periodo == "dia":
        datestr = "%d de %B de %Y"
    elif periodo == "sem":
        datestr = "%Y, semana %W"

    return pg.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=[i for i in tbl[date_col]],
            ticktext=[i.strftime(datestr) for i in tbl[date_col]],
            showticklabels=False,
        ),
        yaxis_tickprefix="R$",
        yaxis_tickformat=" ",
    )


def _gerar_layout_vazio():
    """
    Retorna um `plotly.graph_objects.Layout` sem marcadores de eixos
    """
    return pg.Layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="none",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )


def mensagem(msg: str):
    layout = _gerar_layout_vazio()
    fig = pg.Figure(layout=layout)
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="Nenhum dado disponível",
        showarrow=False,
        font=dict(size=20),
    )
    return fig


def balancos(periodo, n):
    tbl = _preprocessar_data(
        tbl=db.saldos_transac_periodo(periodo=periodo, n=n), periodo=periodo
    )
    if tbl.shape[0] == 0:
        return mensagem("Sem dados para exibir")

    tbl["SomasDisplay"] = tbl["Somas"].apply(
        lambda x: f"{x:_.2f}".replace(".", ",").replace("_", " ")
    )
    tbl["AbatDisplay"] = tbl["Abatimentos"].apply(
        lambda x: f"{x:_.2f}".replace(".", ",").replace("_", " ")
    )

    layout = _gerar_layout(tbl, periodo)

    fig = pg.Figure(layout=layout)
    fig.add_trace(
        pg.Bar(
            x=tbl["Data"],
            y=tbl["Somas"],
            name="Somas",
            customdata=tbl[["SomasDisplay"]],
            hovertemplate="<b>R$ %{customdata[0]}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[1]),
        )
    )
    fig.add_trace(
        pg.Bar(
            x=tbl["Data"],
            y=tbl["Abatimentos"],
            name="Abatimentos",
            customdata=tbl[["AbatDisplay"]],
            hovertemplate="<b>R$ %{customdata[0]}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[0]),
        )
    )
    fig._config["displayModeBar"] = False
    return fig


def saldo_acum(periodo, n):
    tbl = _preprocessar_data(
        tbl=db.saldos_transac_periodo(periodo=periodo, n=n), periodo=periodo
    )
    if tbl.shape[0] == 0:
        return mensagem("Sem dados para exibir")

    tbl["SaldoAcum"] = (tbl["Somas"] + tbl["Abatimentos"]).cumsum()
    tbl["SaldoAcumDisplay"] = tbl["SaldoAcum"].apply(
        lambda x: f"{x:_.2f}".replace(".", ",").replace("_", " ")
    )

    layout = _gerar_layout(tbl, periodo)

    fig = pg.Figure(layout=layout)
    fig.add_trace(
        pg.Scatter(
            x=tbl["Data"],
            y=tbl["SaldoAcum"],
            name="Saldo",
            mode="lines+markers",
            customdata=tbl[["SaldoAcumDisplay"]],
            hovertemplate="<b>R$ %{customdata[0]}</b>",
            offsetgroup=0,
            marker=dict(color=CORES[0]),
        )
    )
    fig.update_xaxes(showgrid=False)
    fig._config["displayModeBar"] = False
    return fig
