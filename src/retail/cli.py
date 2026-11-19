import argparse
import sys
from pathlib import Path

import pandas as pd

from .charts import report_html
from .clean import clean
from .download import download
from .export import build, write


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="retail")
    parser.add_argument("--data", type=Path, default=Path("data"))
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("download", help="télécharge le jeu de données (45 Mo)")
    p = sub.add_parser("build", help="nettoie, analyse et exporte les résultats")
    p.add_argument("--out", type=Path, default=Path("export/retail.json"))
    p.add_argument("--report", type=Path, default=Path("reports/rapport.html"))
    args = parser.parse_args(argv)

    if args.cmd == "download":
        print(download(args.data))
        return 0

    raw = pd.read_parquet(download(args.data))
    cleaned = clean(raw)
    for rule in cleaned.rules:
        print(f"{rule.rows:>9,}  {rule.label}".replace(",", " "))
    print(f"{len(cleaned.sales):>9,}  lignes de vente retenues sur {cleaned.raw_rows:,}"
          .replace(",", " "))
    data = build(cleaned)
    write(data, args.out)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report_html(data), encoding="utf-8")
    print(f"\n{args.out}\n{args.report}\n")
    for line in data["insights"]["fr"]:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
