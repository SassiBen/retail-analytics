from retail.clean import PRODUCT_CODE, clean


def test_rules_are_counted_in_order(raw):
    c = clean(raw)
    assert [(r.name, r.rows) for r in c.rules] == [
        ("doublons", 1), ("annulations", 1), ("hors_catalogue", 1), ("quantite_ou_prix", 1)]
    assert len(c.sales) == 8
    assert c.raw_rows == len(raw)


def test_returns_are_kept_aside(raw):
    c = clean(raw)
    assert list(c.returns["invoice"]) == ["C1003"]
    assert c.returns["revenue"].iloc[0] < 0


def test_revenue_and_customer_type(raw):
    c = clean(raw)
    assert round(c.sales["revenue"].sum(), 2) == round(
        6 * 2.55 + 6 * 3.39 + 4 * 2.55 + 2 * 3.39 + 12 * 2.55 + 12 * 3.39 + 12.75 + 12.75, 2)
    assert str(c.sales["customer_id"].dtype) == "Int64"


def test_product_codes():
    assert PRODUCT_CODE.match("85123A") and PRODUCT_CODE.match("71053")
    assert not PRODUCT_CODE.match("POST") and not PRODUCT_CODE.match("BANK CHARGES")
