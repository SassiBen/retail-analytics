"""Export des résultats pour la page web : un JSON compact et autoportant.

Les phrases d'analyse sont calculées à partir des chiffres, pas écrites à la
main : si le nettoyage ou les données changent, le texte suit.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from . import analyses
from .clean import Cleaned
from .db import connect, query

WEEKDAYS = {"fr": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
            "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}


def _title(s: str | None) -> str:
    return (s or "").strip().capitalize()


def _pct(x: float, lang: str) -> str:
    v = f"{x * 100:.0f} %" if lang == "fr" else f"{x * 100:.0f}%"
    return v


def insights(data: dict) -> dict[str, list[str]]:
    monthly = pd.DataFrame(data["monthly"])
    y2010 = monthly[monthly["month"].str.startswith("2010")]
    nov = y2010.loc[y2010["month"] == "2010-11", "revenue"].sum()
    q4 = y2010[y2010["month"] >= "2010-09"]["revenue"].sum()
    q4_share = q4 / y2010["revenue"].sum()
    uk = next((c for c in data["countries"] if c["country"] == "United Kingdom"), None)
    uk_share = uk["revenue"] / data["kpis"]["revenue"] if uk else 0.0
    p = data["pareto"]
    champions = next((s for s in data["rfm"] if s["segment"] == "champions"),
                     {"customer_share": 0.0, "revenue_share": 0.0})
    m1 = sum(row[1] for row in data["cohorts"]["matrix"] if len(row) > 1) / max(
        sum(1 for row in data["cohorts"]["matrix"] if len(row) > 1), 1)
    saturday = sum(data["heatmap"]["values"][5])
    saturday_share = saturday / max(sum(map(sum, data["heatmap"]["values"])), 1)
    best = data["basket"][0] if data["basket"] else None

    out = {"fr": [], "en": []}
    out["fr"].append(f"De septembre à décembre, l'activité concentre {_pct(q4_share, 'fr')} du "
                     f"chiffre d'affaires de l'année 2010 ; novembre à lui seul en pèse "
                     f"{_pct(nov / y2010['revenue'].sum(), 'fr')}. Le stock et la logistique "
                     "se dimensionnent sur ce pic.")
    out["en"].append(f"September to December brings in {_pct(q4_share, 'en')} of 2010 revenue; "
                     f"November alone accounts for {_pct(nov / y2010['revenue'].sum(), 'en')}. "
                     "Stock and logistics have to be sized for that peak.")
    out["fr"].append(f"{_pct(p['share_of_products_for_80pct'], 'fr')} des références font 80 % "
                     "du chiffre d'affaires : le reste du catalogue est une longue traîne.")
    out["en"].append(f"{_pct(p['share_of_products_for_80pct'], 'en')} of products make 80% of "
                     "revenue; the rest of the catalogue is a long tail.")
    out["fr"].append(f"Les « champions » (achats récents et fréquents) sont "
                     f"{_pct(champions['customer_share'], 'fr')} des clients et rapportent "
                     f"{_pct(champions['revenue_share'], 'fr')} du chiffre d'affaires.")
    out["en"].append(f"“Champions” (recent, frequent buyers) are "
                     f"{_pct(champions['customer_share'], 'en')} of customers and bring in "
                     f"{_pct(champions['revenue_share'], 'en')} of revenue.")
    out["fr"].append(f"En moyenne, {_pct(m1, 'fr')} des nouveaux clients reviennent le mois "
                     "suivant leur premier achat : c'est le levier de fidélisation à travailler.")
    out["en"].append(f"On average, {_pct(m1, 'en')} of new customers come back the month after "
                     "their first order: that is the retention lever to work on.")
    out["fr"].append(f"Le Royaume-Uni représente {_pct(uk_share, 'fr')} des ventes ; "
                     "l'export reste un relais de croissance.")
    out["en"].append(f"The United Kingdom accounts for {_pct(uk_share, 'en')} of sales; "
                     "exports remain a growth lever.")
    if saturday_share < 0.01:
        orders = data["kpis"]["orders"]
        orders_fr = f"{orders:,}".replace(",", "\u202f")
        out["fr"].append(f"Le samedi ne compte que {saturday} commandes sur {orders_fr} : "
                         "l'activité tourne du dimanche au vendredi, avec un pic le jeudi.")
        out["en"].append(f"Saturday accounts for only {saturday} orders out of {orders:,}: "
                         "the business runs Sunday to Friday, peaking on Thursday.")
    if best:
        out["fr"].append(f"Paire la plus liée : « {best['a']} » et « {best['b']} », achetés "
                         f"ensemble {best['lift']:.0f} fois plus souvent que le hasard.")
        out["en"].append(f"Strongest pair: “{best['a']}” and “{best['b']}”, bought together "
                         f"{best['lift']:.0f} times more often than chance.")
    return out


def build(cleaned: Cleaned) -> dict:
    con = connect(cleaned.sales, cleaned.returns)
    k = analyses.kpis(con)
    cohorts = analyses.cohort_matrix(con)
    p = analyses.pareto(con)
    heat = analyses.heatmap(con)
    pairs = analyses.basket_pairs(con)

    data = {
        "meta": {
            "dataset": "Online Retail II",
            "source": "UCI Machine Learning Repository",
            "doi": "10.24432/C5CG6D",
            "license": "CC BY 4.0",
            "currency": "GBP",
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%d"),
            "rows_raw": cleaned.raw_rows,
            "rows_clean": len(cleaned.sales),
        },
        "quality": [{"rule": r.name, "label": r.label, "rows": r.rows} for r in cleaned.rules],
        "kpis": {
            "revenue": round(float(k["revenue"])),
            "orders": int(k["orders"]),
            "customers": int(k["customers"]),
            "avg_order_value": round(float(k["avg_order_value"]), 2),
            "products": int(k["products"]),
            "countries": int(k["countries"]),
            "return_rate": round(k["return_rate"], 4) if k["return_rate"] is not None else None,
            "first_date": str(k["first_date"])[:10],
            "last_date": str(k["last_date"])[:10],
        },
        "monthly": [
            {"month": r.month, "revenue": round(r.revenue), "orders": int(r.orders),
             "customers": int(r.customers)}
            for r in query(con, "monthly").itertuples()
        ],
        "countries": [
            {"country": r.country, "revenue": round(r.revenue), "orders": int(r.orders),
             "customers": int(r.customers)}
            for r in query(con, "countries").itertuples()
        ][:12],
        "cohorts": {
            "cohorts": list(cohorts.index),
            "matrix": [[round(float(v), 3) for v in row if pd.notna(v)]
                       for row in cohorts.to_numpy()],
        },
        "rfm": [
            {"segment": r.segment, "customers": int(r.customers),
             "customer_share": round(r.customer_share, 4),
             "revenue_share": round(r.revenue_share, 4),
             "recency_median": round(float(r.recency_median)),
             "frequency_median": round(float(r.frequency_median), 1)}
            for r in analyses.rfm_summary(con).itertuples()
        ],
        "pareto": {
            "products": p["products"],
            "products_for_80pct": p["products_for_80pct"],
            "share_of_products_for_80pct": round(p["share_of_products_for_80pct"], 4),
            "curve": [[round(x, 4), round(y, 4)] for x, y in p["curve"]],
            "top": [{"code": r.stock_code, "name": _title(r.description),
                     "revenue": round(r.revenue)} for r in p["top"].itertuples()],
        },
        "heatmap": {
            "days": WEEKDAYS,
            "hours": [int(h) for h in heat.columns],
            "values": heat.to_numpy().tolist(),
        },
        "basket": [
            {"a": _title(r.a_name), "b": _title(r.b_name), "together": int(r.together),
             "support": round(r.support, 4), "confidence": round(r.confidence, 3),
             "lift": round(r.lift, 1)}
            for r in pairs.itertuples()
        ],
    }
    data["insights"] = insights(data)
    return data


def write(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
