"""Graphiques Plotly, partagés par le rapport HTML et le tableau de bord."""

import plotly.graph_objects as go

WINE = "#6B0F1A"
WINE_SOFT = "#C7798A"
INK = "#1A0E11"
SEGMENT_LABELS = {"champions": "Champions", "fideles": "Fidèles", "nouveaux": "Nouveaux",
                  "a_relancer": "À relancer", "a_risque": "À risque", "endormis": "Endormis"}


def _layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(title=title, template="simple_white", font={"color": INK},
                      margin={"l": 50, "r": 20, "t": 60, "b": 40}, height=380)
    return fig


def monthly(data: dict) -> go.Figure:
    m = data["monthly"]
    fig = go.Figure(go.Bar(x=[r["month"] for r in m], y=[r["revenue"] for r in m],
                           marker_color=WINE))
    return _layout(fig, "Chiffre d'affaires mensuel (£)")


def cohorts(data: dict) -> go.Figure:
    c = data["cohorts"]
    z = [[v * 100 for v in row] for row in c["matrix"]]
    fig = go.Figure(go.Heatmap(z=z, y=c["cohorts"], x=list(range(len(z[0]))),
                               colorscale=[[0, "#FAF8F7"], [1, WINE]], zmax=50,
                               hovertemplate="%{y} · M+%{x} : %{z:.0f} %<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, "Rétention par cohorte (% des clients revenus)")


def rfm(data: dict) -> go.Figure:
    seg = data["rfm"]
    labels = [SEGMENT_LABELS[s["segment"]] for s in seg]
    fig = go.Figure([
        go.Bar(name="Clients", x=labels, y=[s["customer_share"] * 100 for s in seg],
               marker_color=WINE_SOFT),
        go.Bar(name="Chiffre d'affaires", x=labels, y=[s["revenue_share"] * 100 for s in seg],
               marker_color=WINE),
    ])
    fig.update_layout(barmode="group")
    return _layout(fig, "Segments RFM (% du total)")


def pareto(data: dict) -> go.Figure:
    curve = data["pareto"]["curve"]
    fig = go.Figure(go.Scatter(x=[p[0] * 100 for p in curve], y=[p[1] * 100 for p in curve],
                               mode="lines", line={"color": WINE, "width": 3}))
    fig.add_hline(y=80, line_dash="dot")
    fig.update_xaxes(title="% des références")
    fig.update_yaxes(title="% du chiffre d'affaires cumulé")
    return _layout(fig, "Concentration du chiffre d'affaires")


def heatmap(data: dict) -> go.Figure:
    h = data["heatmap"]
    fig = go.Figure(go.Heatmap(z=h["values"], x=[f"{x} h" for x in h["hours"]],
                               y=h["days"]["fr"], colorscale=[[0, "#FAF8F7"], [1, WINE]]))
    fig.update_yaxes(autorange="reversed")
    return _layout(fig, "Commandes par jour et par heure")


ALL = [monthly, cohorts, rfm, pareto, heatmap]


def report_html(data: dict) -> str:
    parts = [f(data).to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False)
             for i, f in enumerate(ALL)]
    bullets = "".join(f"<li>{s}</li>" for s in data["insights"]["fr"])
    return (
        "<!doctype html><html lang='fr'><meta charset='utf-8'><title>Online Retail II</title>"
        "<body style='font-family:system-ui;max-width:1000px;margin:auto;padding:24px'>"
        "<h1>Online Retail II : ce que disent les ventes</h1>"
        f"<ul>{bullets}</ul>{''.join(parts)}</body></html>"
    )
