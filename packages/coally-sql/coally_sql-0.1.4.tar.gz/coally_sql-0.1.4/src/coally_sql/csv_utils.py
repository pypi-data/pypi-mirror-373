from __future__ import annotations

import csv
import sys
import pandas as pd

# Allow very large CSV fields (e.g., huge JSON in a single cell)
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(10**9)


def smart_read_csv(path, encodings=("utf-8", "utf-8-sig", "latin1")):
    """
    Robust CSV reader:
    - Delimiter heuristics: \t, ',', ';', '|'
    - Try engine='c' first (fast), then engine='python'
    - on_bad_lines='skip' to survive broken rows
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        sample = "".join([f.readline() for _ in range(10)])

    candidates = ["\t", ",", ";", "|"]
    candidates.sort(key=lambda s: sample.count(s), reverse=True)

    last_err = None

    # 1) Fast C engine
    for enc in encodings:
        for sep in candidates:
            try:
                df = pd.read_csv(
                    path, sep=sep, engine="c", encoding=enc,
                    quoting=csv.QUOTE_MINIMAL, on_bad_lines="skip"
                )
                if df.shape[1] > 1:
                    return df
            except Exception as e:
                last_err = e

    # 2) Fallback Python engine
    for enc in encodings:
        for sep in candidates + [None]:  # None = auto heuristic
            try:
                df = pd.read_csv(
                    path, sep=sep, engine="python", encoding=enc,
                    quoting=csv.QUOTE_MINIMAL, on_bad_lines="skip"
                )
                if df.shape[1] > 1:
                    return df
            except Exception as e:
                last_err = e

    raise RuntimeError(f"Could not parse CSV, last error: {last_err}")
