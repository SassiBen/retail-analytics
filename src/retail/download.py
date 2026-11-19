"""Téléchargement du jeu Online Retail II (UCI Machine Learning Repository).

Transactions réelles d'un e-commerçant britannique de cadeaux et d'objets de
décoration, de décembre 2009 à décembre 2011. Licence CC BY 4.0.
Chen, D. (2019). Online Retail II. https://doi.org/10.24432/C5CG6D
"""

import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"

COLUMNS = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def download(dest: Path) -> Path:
    """Télécharge l'archive et la convertit en Parquet (lire 1 M de lignes Excel prend
    plusieurs minutes, le Parquet se relit en une seconde)."""
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "online_retail_ii.parquet"
    if out.exists():
        return out
    archive_path = dest / "online_retail_ii.zip"
    if not archive_path.exists():
        urllib.request.urlretrieve(URL, archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        xlsx = next(n for n in archive.namelist() if n.endswith(".xlsx"))
        # Les codes et libellés doivent rester du texte : Excel stocke certains
        # libellés purement numériques comme des nombres.
        sheets = pd.read_excel(archive.open(xlsx), sheet_name=None,
                               dtype={"Invoice": str, "StockCode": str, "Description": str})
    df = pd.concat(sheets.values(), ignore_index=True).rename(columns=COLUMNS)
    df["country"] = df["country"].astype(str)
    df.to_parquet(out, index=False)
    return out
