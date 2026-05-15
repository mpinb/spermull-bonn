"""Filter and normalize a Bonn Sperrmüll schedule CSV to a canonical format.

Ported from the manual exploration in py/parse_data.ipynb — see that notebook
for context on the data source.

Usage:
    python filter_spermull.py [--input PATH] [--output PATH]

Defaults:
    --input   <repo>/data/spermullterminebonn2026.csv
    --output  <repo>/data/spermull_only_2026.csv

The script:
  - Auto-detects the field separator (';' or ',')
  - Keeps only rows where PLAN_BEZ == 'Sperrmüll'
  - Retains: ID_TERMINE, PLAN_BEZ, STRASSE1, ORTSTEIL1, PLZ1,
             HNR_GE_AB, HNR_GE_BIS, HNR_UG_AB, HNR_UG_BIS
  - Collects all non-empty TERMIN* values per row and renumbers them
    TERMIN001 … TERMIN00N  (N = max non-empty count across all rows)
  - Converts dates from DD.MM.YYYY to YYYY-MM-DD where necessary
  - Writes a comma-separated output CSV with no extra index column
"""

import argparse
import os
import re

import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "data"))

BASE_COLUMNS = [
    "ID_TERMINE",
    "PLAN_BEZ",
    "STRASSE1",
    "ORTSTEIL1",
    "PLZ1",
    "HNR_GE_AB",
    "HNR_GE_BIS",
    "HNR_UG_AB",
    "HNR_UG_BIS",
]

_GERMAN_DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def detect_separator(path: str) -> str:
    """Return ';' or ',' based on the first line of the file."""
    with open(path, "r", encoding="utf-8-sig") as fh:
        first_line = fh.readline()
    return ";" if ";" in first_line else ","


def to_iso_date(value: str) -> str:
    """Convert DD.MM.YYYY → YYYY-MM-DD; pass through anything else unchanged."""
    if isinstance(value, str) and _GERMAN_DATE_RE.match(value.strip()):
        day, month, year = value.strip().split(".")
        return f"{year}-{month}-{day}"
    return value


def normalize_termins(df: pd.DataFrame) -> pd.DataFrame:
    """Collect non-empty TERMIN* values per row, convert date format, and
    renumber the columns as TERMIN001 … TERMIN00N."""
    termin_cols = sorted(
        [c for c in df.columns if re.match(r"^TERMIN\d+$", c)],
        key=lambda c: int(c[6:]),
    )

    def collect(row):
        return [
            to_iso_date(str(v))
            for v in row[termin_cols]
            if pd.notna(v) and str(v).strip() != ""
        ]

    series = df.apply(collect, axis=1)
    max_n = series.apply(len).max() if len(series) > 0 else 0

    df = df.drop(columns=termin_cols)

    for i in range(1, max_n + 1):
        col = f"TERMIN{i:03d}"
        df[col] = series.apply(lambda x, idx=i - 1: x[idx] if idx < len(x) else None)

    return df


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Filter a Sperrmüll schedule CSV to only Sperrmüll rows "
            "and normalize it to a canonical format."
        )
    )
    parser.add_argument(
        "--input",
        default=os.path.join(_DATA_DIR, "spermullterminebonn2026.csv"),
        help="Path to the raw schedule CSV (default: data/spermullterminebonn2026.csv)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(_DATA_DIR, "spermull_only_2026.csv"),
        help="Path for the normalized output CSV (default: data/spermull_only_2026.csv)",
    )
    args = parser.parse_args()

    sep = detect_separator(args.input)
    print(f"Detected separator: {repr(sep)}")

    df = pd.read_csv(
        args.input,
        sep=sep,
        encoding="utf-8-sig",
        dtype={
            "HNR_GE_AB": "Int64",
            "HNR_GE_BIS": "Int64",
            "HNR_UG_AB": "Int64",
            "HNR_UG_BIS": "Int64",
        },
        low_memory=False,
    )
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns.")

    df = df[df["PLAN_BEZ"] == "Sperrmüll"].copy()
    print(f"After PLAN_BEZ filter: {len(df)} rows.")

    missing = [c for c in BASE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV is missing expected columns: {missing}")

    termin_cols = sorted(
        [c for c in df.columns if re.match(r"^TERMIN\d+$", c)],
        key=lambda c: int(c[6:]),
    )
    df = df[BASE_COLUMNS + termin_cols].copy()

    df = normalize_termins(df)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(args.output, index=False)

    new_termin_cols = [c for c in df.columns if re.match(r"^TERMIN\d+$", c)]
    print(
        f"Written {len(df)} rows, {len(new_termin_cols)} TERMIN column(s) "
        f"→ {args.output}"
    )


if __name__ == "__main__":
    main()
