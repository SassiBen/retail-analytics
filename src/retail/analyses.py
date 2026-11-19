import duckdb
import pandas as pd

from .db import query

SEGMENTS = ["champions", "fideles", "nouveaux", "a_relancer", "a_risque", "endormis"]


def kpis(con: duckdb.DuckDBPyConnection) -> dict:
    k = query(con, "kpis").iloc[0].to_dict()
    try:
        r = query(con, "returns").iloc[0].to_dict()
        k["return_rate"] = float(r["returned_value"] or 0) / float(k["revenue"])
    except duckdb.CatalogException:
        k["return_rate"] = None
    return k


def cohort_matrix(con: duckdb.DuckDBPyConnection, months: int = 12) -> pd.DataFrame:
    """Part (0-1) des clients de chaque cohorte encore actifs N mois plus tard."""
    df = query(con, "cohorts")
    pivot = df.pivot(index="cohort", columns="month_offset", values="customers").fillna(0)
    sizes = pivot[0]
    return pivot.div(sizes, axis=0).loc[:, :months - 1]


def rfm_summary(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    rfm = query(con, "rfm")
    total_customers = len(rfm)
    total_revenue = rfm["monetary"].sum()
    g = rfm.groupby("segment").agg(
        customers=("customer_id", "count"),
        revenue=("monetary", "sum"),
        recency_median=("recency", "median"),
        frequency_median=("frequency", "median"),
    )
    g["customer_share"] = g["customers"] / total_customers
    g["revenue_share"] = g["revenue"] / total_revenue
    return g.reindex([s for s in SEGMENTS if s in g.index]).reset_index()


def pareto(con: duckdb.DuckDBPyConnection, points: int = 50) -> dict:
    products = query(con, "products")
    share = products["revenue"].cumsum() / products["revenue"].sum()
    n = len(products)
    top_80 = int((share < 0.8).sum()) + 1
    idx = sorted({min(n - 1, round(i * (n - 1) / (points - 1))) for i in range(points)})
    return {
        "products": n,
        "products_for_80pct": top_80,
        "share_of_products_for_80pct": top_80 / n,
        "curve": [[(i + 1) / n, float(share.iloc[i])] for i in idx],
        "top": products.head(10),
    }


def heatmap(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = query(con, "heatmap")
    return df.pivot(index="weekday", columns="hour", values="orders").reindex(
        range(1, 8)).fillna(0).astype(int)


def basket_pairs(con: duckdb.DuckDBPyConnection, min_together: int = 150,
                 limit: int = 15) -> pd.DataFrame:
    pairs = query(con, "basket", min_together=min_together, limit=limit)
    names = query(con, "products").set_index("stock_code")["description"]
    return pairs.assign(a_name=pairs["a"].map(names), b_name=pairs["b"].map(names))
