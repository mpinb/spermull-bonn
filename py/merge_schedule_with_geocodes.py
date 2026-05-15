"""Merge a normalized Sperrmüll schedule CSV with geocoded addresses and
produce the geo_dates.msg msgpack file consumed by the Flask app.

Ported from py/date_to_geocode.ipynb — see that notebook for the original
exploratory implementation and inline comments on the data joining logic.

Usage:
    python merge_schedule_with_geocodes.py [--schedule PATH] [--geocodes PATH] [--output PATH]

Defaults:
    --schedule  <repo>/data/spermull_only_2026.csv
    --geocodes  <repo>/data/geocoded_addr.csv
    --output    <repo>/data/geo_dates.msg
"""

import argparse
import os
import re

import pandas as pd
from isf_pandas_msgpack import to_msgpack

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "data"))


def hn_in_range(row: pd.Series) -> bool:
    """Return True if the geocoded house number falls within the schedule's range.

    Even house numbers are checked against the GE (gerade = even) range,
    odd house numbers against the UG (ungerade = odd) range.
    Sentinel value 9999/9998 in the upper-bound columns means 'no upper limit'.
    Rows with NA in any required range column are excluded.
    """
    hn = row["HNR"]
    if pd.isna(hn):
        return False
    hn = int(hn)
    lo, hi = (row["HNR_GE_AB"], row["HNR_GE_BIS"]) if hn % 2 == 0 else (row["HNR_UG_AB"], row["HNR_UG_BIS"])
    if pd.isna(lo) or pd.isna(hi):
        return False
    return int(lo) <= hn <= int(hi)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Merge a Sperrmüll schedule CSV with geocoded addresses "
            "and write geo_dates.msg for the Flask app."
        )
    )
    parser.add_argument(
        "--schedule",
        default=os.path.join(_DATA_DIR, "spermull_only_2026.csv"),
        help="Normalized schedule CSV (default: data/spermull_only_2026.csv)",
    )
    parser.add_argument(
        "--geocodes",
        default=os.path.join(_DATA_DIR, "geocoded_addr.csv"),
        help="Geocoded addresses CSV (default: data/geocoded_addr.csv)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(_DATA_DIR, "geo_dates.msg"),
        help="Output msgpack path (default: data/geo_dates.msg)",
    )
    args = parser.parse_args()

    # Load schedule (output of filter_spermull.py)
    schedule = pd.read_csv(
        args.schedule,
        dtype={
            "PLZ1": "Int64",
            "HNR_GE_AB": "Int64",
            "HNR_GE_BIS": "Int64",
            "HNR_UG_AB": "Int64",
            "HNR_UG_BIS": "Int64",
        },
    )

    # Load geocoded addresses (produced by py/extract_addresses.ipynb)
    geocodes = pd.read_csv(
        args.geocodes,
        index_col=0,
        dtype={"PLZ1": "Int64", "HNR": "Int64"},
    )

    print(f"Schedule: {len(schedule)} rows; geocodes: {len(geocodes)} rows.")

    # Inner join on postal code + street name
    merged = pd.merge(geocodes, schedule, on=["PLZ1", "STRASSE1"])
    print(f"After join: {len(merged)} rows.")

    # Filter to addresses whose house number falls within the schedule's range
    filtered = merged[merged.apply(hn_in_range, axis=1)].copy()
    print(f"After house-number filter: {len(filtered)} rows.")

    # Detect all TERMIN columns dynamically — works for any number of pickups per year
    termin_cols = sorted(
        [c for c in filtered.columns if re.match(r"^TERMIN\d+$", c)],
        key=lambda c: int(c[6:]),
    )
    if not termin_cols:
        raise ValueError("No TERMIN* columns found in the schedule file.")
    print(
        f"Melting {len(termin_cols)} TERMIN column(s): "
        f"{termin_cols[0]} … {termin_cols[-1]}"
    )

    # Melt all date columns into a single 'date' column
    melted = filtered.melt(
        id_vars=["LAT", "LON"],
        value_vars=termin_cols,
        var_name="termin_nr",
        value_name="date",
    )
    melted = melted.dropna(subset=["date"]).reset_index(drop=True)

    # Build MultiIndex [date, row_index], convert date level to datetime, sort
    melted.set_index(["date", melted.index], inplace=True)
    melted.index = melted.index.set_levels(
        pd.to_datetime(melted.index.levels[0]), level=0
    )
    melted.sort_index(inplace=True)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    to_msgpack(args.output, melted)
    print(f"Written {len(melted)} records → {args.output}")


if __name__ == "__main__":
    main()
