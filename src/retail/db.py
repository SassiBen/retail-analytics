from importlib import resources

import duckdb
import pandas as pd


def connect(sales: pd.DataFrame, returns: pd.DataFrame | None = None) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.register("sales_df", sales)
    con.execute("CREATE TABLE sales AS SELECT * FROM sales_df")
    if returns is not None:
        con.register("returns_df", returns)
        con.execute("CREATE TABLE returns AS SELECT * FROM returns_df")
    return con


def query(con: duckdb.DuckDBPyConnection, name: str, **params) -> pd.DataFrame:
    sql = resources.files("retail").joinpath("sql", f"{name}.sql").read_text(encoding="utf-8")
    return con.execute(sql, params or None).df()
