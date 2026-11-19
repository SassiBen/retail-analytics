import pytest

from retail import analyses
from retail.clean import clean
from retail.db import connect


@pytest.fixture
def con(raw):
    c = clean(raw)
    return connect(c.sales, c.returns)


def test_kpis(con):
    k = analyses.kpis(con)
    assert k["orders"] == 6
    assert k["customers"] == 3
    assert k["return_rate"] == pytest.approx(2 * 2.55 / k["revenue"])


def test_cohort_retention(con):
    m = analyses.cohort_matrix(con)
    # cohorte de janvier : clients 1 et 2 ; seul le 1 revient en M+1 et M+2
    assert list(m.loc["2010-01"].iloc[:3]) == [1.0, 0.5, 0.5]
    assert m.loc["2010-02"].iloc[0] == 1.0


def test_rfm_segments_cover_every_identified_customer(con):
    s = analyses.rfm_summary(con)
    assert s["customers"].sum() == 3
    assert s["revenue_share"].sum() == pytest.approx(1.0)


def test_pareto(con):
    p = analyses.pareto(con, points=5)
    assert p["products"] == 3
    assert 1 <= p["products_for_80pct"] <= 3
    assert p["curve"][-1][1] == pytest.approx(1.0)


def test_heatmap_has_seven_days(con):
    h = analyses.heatmap(con)
    assert list(h.index) == list(range(1, 8))
    assert h.to_numpy().sum() == 6


def test_basket_lift(con):
    pairs = analyses.basket_pairs(con, min_together=1)
    top = pairs.iloc[0]
    assert {top["a"], top["b"]} == {"71053", "85123A"}
    # présents ensemble dans les 2 paniers de 2 articles ou plus : lift = 2*2/(2*2) = 1
    assert top["lift"] == pytest.approx(1.0)


def test_rfm_is_deterministic(con):
    from retail.db import query
    first = query(con, "rfm").sort_values("customer_id").reset_index(drop=True)
    for _ in range(3):
        again = query(con, "rfm").sort_values("customer_id").reset_index(drop=True)
        assert first[["r", "f", "m", "segment"]].equals(again[["r", "f", "m", "segment"]])
