from retail.clean import clean
from retail.export import build


def test_export_is_complete_and_serialisable(raw):
    import json
    data = build(clean(raw))
    assert set(data) >= {"meta", "quality", "kpis", "monthly", "cohorts", "rfm", "pareto",
                         "heatmap", "basket", "insights"}
    assert len(data["heatmap"]["values"]) == 7
    assert len(data["insights"]["fr"]) == len(data["insights"]["en"])
    json.dumps(data)
