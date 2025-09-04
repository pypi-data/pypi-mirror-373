# coally_sql/csv_utils.py
from __future__ import annotations

import csv
import sys
import os
import re
import warnings
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict
from collections import defaultdict

import pandas as pd
from pandas.errors import DtypeWarning


# Allow very large CSV fields (e.g., huge JSON in a single cell)
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(10**9)


class CsvValidationError(Exception):
    """Raised when CSV validation finds blocking issues (fail-fast)."""
    pass


@dataclass
class Finding:
    code: str              # e.g., C010, D100
    severity: str          # "error" | "warn"
    column_original: str | None
    column_final: str | None
    details: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


_SQL_RESERVED = {
    "select","from","where","group","order","by","limit","offset",
    "insert","update","delete","join","on","create","table","view",
    "index","drop","alter","and","or","not","as"
}

_NUMERIC_RE = re.compile(r"^[+-]?(\d+(\.\d+)?|\.\d+)$")
_ALNUM_RE = re.compile(r"[A-Za-z]")
_NON_ALNUM_TO_UNDERSCORE = re.compile(r"[^a-z0-9]+")


# ---------------------------------------------------------------------
# Smart CSV reader (delimiter/encoding heuristics, skip bad rows)
# ---------------------------------------------------------------------
def smart_read_csv(path, encodings=("utf-8", "utf-8-sig", "latin1")) -> pd.DataFrame:
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
                    quoting=csv.QUOTE_MINIMAL, on_bad_lines="skip",
                    dtype=str, low_memory=False
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
                    quoting=csv.QUOTE_MINIMAL, on_bad_lines="skip",
                    dtype=str, low_memory=False
                )
                if df.shape[1] > 1:
                    return df
            except Exception as e:
                last_err = e

    raise RuntimeError(f"Could not parse CSV, last error: {last_err}")


# ---------------------------------------------------------------------
# Validators & helpers
# ---------------------------------------------------------------------
def _normalize_name(col: str) -> str:
    s = ("" if col is None else str(col)).lower()
    s = _NON_ALNUM_TO_UNDERSCORE.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "col"

def _looks_numeric(s: Optional[str]) -> bool:
    if s is None:
        return False
    s = str(s).strip()
    if not s:
        return False
    return bool(_NUMERIC_RE.match(s))

def _looks_alpha(s: Optional[str]) -> bool:
    if s is None:
        return False
    return bool(_ALNUM_RE.search(str(s)))

def _detect_mixed_content(df: pd.DataFrame, sample_rows: int = 500) -> List[Finding]:
    findings: List[Finding] = []
    if df.empty:
        return findings
    sample = df.head(sample_rows)
    for col in sample.columns:
        vals = sample[col].dropna().astype(str).str.strip()
        if vals.empty:
            continue
        any_numeric = any(_looks_numeric(v) for v in vals if v != "")
        any_alpha = any((_looks_alpha(v) and not _looks_numeric(v)) for v in vals if v != "")
        if any_numeric and any_alpha:
            findings.append(Finding(
                code="D100",
                severity="warn",
                column_original=col,
                column_final=col,
                details="Mixed content (numeric-like and non-numeric-like). Imported as TEXT; cast explicitly in SQL."
            ))
    return findings

def _validate_and_fix_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Finding]]:
    findings: List[Finding] = []
    original = list(df.columns)

    for c in original:
        if c is None or str(c).strip() == "":
            findings.append(Finding("C020", "error", str(c), None, "Empty column name"))

    normalized = [_normalize_name(c) for c in original]

    for o, n in zip(original, normalized):
        if n in _SQL_RESERVED:
            findings.append(Finding("C040", "warn", str(o), n, "Column normalized to a SQL keyword; consider renaming."))

    seen: defaultdict[str, int] = defaultdict(int)
    final_cols: List[str] = []
    for o, n in zip(original, normalized):
        seen[n] += 1
        if seen[n] == 1:
            final = n
            if n != o:
                findings.append(Finding("C030", "warn", str(o), final, "Renamed to SQL-safe identifier."))
        else:
            final = f"{n}_{seen[n]}"
            findings.append(Finding("C010", "error", str(o), final, "Duplicate (case-insensitive), suffixed."))

        if len(final) > 128:
            findings.append(Finding("C050", "warn", str(o), final, "Very long column name; consider shortening."))

        final_cols.append(final)

    df = df.copy()
    df.columns = final_cols
    return df, findings

def _format_human_message(findings: List[Finding], report_path: Optional[str]) -> str:
    MAX_LINES = 12
    errors = [f for f in findings if f.severity == "error"]
    warns  = [f for f in findings if f.severity == "warn"]

    lines: List[str] = []
    if errors:
        lines.append("CSV validation failed in coally_sql:\n")
        lines.append("Blocking issues:")
        for f in errors[:MAX_LINES]:
            lines.append(f"  - {f.code} {f.details}: {f.column_original!r} → {f.column_final!r}")
        if len(errors) > MAX_LINES:
            lines.append(f"  ... and {len(errors) - MAX_LINES} more error(s).")
    else:
        lines.append("CSV validation completed with non-blocking notes:")

    if warns:
        lines.append("\nNon-blocking notes:")
        for f in warns[:MAX_LINES]:
            lines.append(f"  - {f.code} {f.details}: {f.column_original!r} → {f.column_final!r}")
        if len(warns) > MAX_LINES:
            lines.append(f"  ... and {len(warns) - MAX_LINES} more note(s).")

    if report_path:
        lines.append("\nA detailed report was written to:")
        lines.append(f"  • {report_path}")

    lines.append("\nTip: all columns are imported as TEXT; cast explicitly in SQL, e.g.:")
    lines.append('  SELECT CAST(info_classification_cvss_score AS REAL) AS score FROM data;')
    return "\n".join(lines)

def _default_report_path(csv_path: str) -> str:
    base = os.path.splitext(os.path.basename(csv_path))[0]
    return os.path.join(os.path.dirname(csv_path), f"{base}__COLUMN_REPORT.csv")

def read_csv_robust(
    path: str,
    *,
    write_report: bool = True,
    report_path: Optional[str] = None,
) -> Tuple[pd.DataFrame, List[Finding]]:
    if report_path is None and write_report:
        report_path = _default_report_path(path)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DtypeWarning)
        df = smart_read_csv(path)

    findings = _detect_mixed_content(df)
    df, col_findings = _validate_and_fix_columns(df)
    findings.extend(col_findings)

    has_error = any(f.severity == "error" for f in findings)

    if write_report and report_path:
        pd.DataFrame([f.to_dict() for f in findings]).to_csv(report_path, index=False)

    if has_error:
        message = _format_human_message(findings, report_path if write_report else None)
        raise CsvValidationError(message)

    return df, findings
