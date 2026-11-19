import pandas as pd
import pytest


def line(invoice, code, qty, price, date, customer, country="United Kingdom", desc=None):
    return {"invoice": invoice, "stock_code": code, "description": desc or f"ART {code}",
            "quantity": qty, "invoice_date": pd.Timestamp(date), "price": price,
            "customer_id": customer, "country": country}


@pytest.fixture
def raw() -> pd.DataFrame:
    rows = [
        # client 1 : achète en janvier, revient en février et en mars
        line("1001", "85123A", 6, 2.55, "2010-01-04 10:00", 1),
        line("1001", "71053", 6, 3.39, "2010-01-04 10:00", 1),
        line("1005", "85123A", 4, 2.55, "2010-02-08 11:00", 1),
        line("1009", "71053", 2, 3.39, "2010-03-01 09:00", 1),
        # client 2 : un seul achat en janvier
        line("1002", "85123A", 12, 2.55, "2010-01-05 14:00", 2, "France"),
        line("1002", "71053", 12, 3.39, "2010-01-05 14:00", 2, "France"),
        # client 3 : arrive en février
        line("1006", "22423", 1, 12.75, "2010-02-10 15:00", 3),
        # bruit à éliminer
        line("1001", "85123A", 6, 2.55, "2010-01-04 10:00", 1),       # doublon exact
        line("C1003", "85123A", -2, 2.55, "2010-01-06 10:00", 1),     # annulation
        line("1004", "POST", 1, 18.0, "2010-01-06 10:00", 2),         # frais de port
        line("1007", "22423", 5, 0.0, "2010-02-11 10:00", None),      # prix nul
        # vente sans client identifié : comptée dans le CA, pas dans les clients
        line("1008", "22423", 1, 12.75, "2010-03-02 16:00", None),
    ]
    df = pd.DataFrame(rows)
    df["customer_id"] = df["customer_id"].astype("Float64")
    return df
