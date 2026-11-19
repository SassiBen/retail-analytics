"""Règles de nettoyage, appliquées dans l'ordre et toutes comptées.

Chaque règle enlève des lignes pour une raison précise, et le rapport dit
combien. Un chiffre d'affaires qui change de 10 % selon qu'on garde ou non les
frais de port ou les annulations doit pouvoir se justifier ligne à ligne.
"""

import re
from dataclasses import dataclass

import pandas as pd

# Un article du catalogue a un code à 5 chiffres, parfois suivi d'une ou deux
# lettres pour la variante (85123A). Le reste désigne des frais, des
# ajustements ou des opérations comptables : POST, DOT, M, BANK CHARGES...
PRODUCT_CODE = re.compile(r"^\d{5}[A-Za-z]{0,2}$")


@dataclass
class Rule:
    name: str
    label: str
    rows: int


@dataclass
class Cleaned:
    sales: pd.DataFrame
    returns: pd.DataFrame
    rules: list[Rule]
    raw_rows: int


def clean(df: pd.DataFrame) -> Cleaned:
    raw_rows = len(df)
    rules: list[Rule] = []
    df = df.copy()
    df["invoice"] = df["invoice"].astype(str).str.strip()
    df["stock_code"] = df["stock_code"].astype(str).str.strip()
    df["description"] = df["description"].astype("string").str.strip()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])

    def drop(mask: pd.Series, name: str, label: str) -> None:
        nonlocal df
        rules.append(Rule(name, label, int(mask.sum())))
        df = df[~mask]

    drop(df.duplicated(), "doublons", "lignes en double exact")

    cancelled = df["invoice"].str.startswith("C")
    returns = df[cancelled].copy()
    drop(cancelled, "annulations", "factures d'annulation (mises de côté comme retours)")

    drop(~df["stock_code"].map(lambda c: bool(PRODUCT_CODE.match(c))),
         "hors_catalogue", "frais de port, ajustements et opérations hors catalogue")
    drop((df["quantity"] <= 0) | (df["price"] <= 0),
         "quantite_ou_prix", "quantité ou prix nul ou négatif (casse, corrections de stock)")

    df = df.assign(revenue=df["quantity"] * df["price"])
    df["customer_id"] = df["customer_id"].astype("Int64")
    returns = returns.assign(revenue=returns["quantity"] * returns["price"])
    returns["customer_id"] = returns["customer_id"].astype("Int64")
    return Cleaned(df.reset_index(drop=True), returns.reset_index(drop=True), rules, raw_rows)
