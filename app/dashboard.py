"""Tableau de bord interactif : streamlit run app/dashboard.py"""

import pandas as pd
import plotly.express as px
import streamlit as st

from retail.clean import clean
from retail.db import connect, query
from retail.download import download

st.set_page_config(page_title="Online Retail II", layout="wide")


@st.cache_data
def load() -> pd.DataFrame:
    return clean(pd.read_parquet(download(__import__("pathlib").Path("data")))).sales


sales = load()
st.title("Online Retail II")

countries = ["Tous"] + sorted(sales["country"].unique())
col1, col2 = st.columns([1, 2])
country = col1.selectbox("Pays", countries)
start, end = col2.slider("Période", value=(sales["invoice_date"].min().to_pydatetime(),
                                            sales["invoice_date"].max().to_pydatetime()))

view = sales[(sales["invoice_date"] >= start) & (sales["invoice_date"] <= end)]
if country != "Tous":
    view = view[view["country"] == country]
con = connect(view)

k = query(con, "kpis").iloc[0]
a, b, c, d = st.columns(4)
a.metric("Chiffre d'affaires", f"£{k['revenue']:,.0f}")
b.metric("Commandes", f"{k['orders']:,}")
c.metric("Clients", f"{k['customers']:,}")
d.metric("Panier moyen", f"£{k['avg_order_value']:,.2f}")

monthly = query(con, "monthly")
st.plotly_chart(px.bar(monthly, x="month", y="revenue", title="Chiffre d'affaires mensuel",
                       color_discrete_sequence=["#6B0F1A"]), use_container_width=True)

left, right = st.columns(2)
rfm = query(con, "rfm")
left.plotly_chart(px.histogram(rfm, x="segment", title="Clients par segment RFM",
                               color_discrete_sequence=["#8E1B2E"]), use_container_width=True)
products = query(con, "products").head(15)
right.plotly_chart(px.bar(products, x="revenue", y="description", orientation="h",
                          title="Meilleures ventes", color_discrete_sequence=["#6B0F1A"]),
                   use_container_width=True)
