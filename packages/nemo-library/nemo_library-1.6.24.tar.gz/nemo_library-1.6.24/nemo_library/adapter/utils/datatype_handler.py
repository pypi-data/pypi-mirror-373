# datatype_handler.py
# Reusable helpers to load CSV files with robust, explicit dtype handling.
#
# Key ideas:
# - Read everything as string first (safe default).
# - Normalize NA-like tokens (e.g., 'NULL').
# - Convert selected columns to nullable numeric types (Int64/Float64).
# - Handle both '.' and ',' as decimal separator for floats.
# - Provide loader functions tailored to the two Zentis files.

from pathlib import Path
from typing import Optional, List
import pandas as pd

# --- NA normalization ---------------------------------------------------------

NA_STRINGS = {None, "", " ", "NULL"}


def normalize_na(df: pd.DataFrame) -> pd.DataFrame:
    """Replace common 'NA-like' string tokens with proper pd.NA in-place and return df.

    We only normalize obvious tokens that come from CSV exports (e.g., 'NULL').
    """
    return df.replace({s: pd.NA for s in NA_STRINGS})


# --- Float parsing with mixed decimal separators ------------------------------


def to_float64_mixed(s: pd.Series) -> pd.Series:
    """Convert a Series of strings to nullable Float64, accepting both '1,23' and '1.23'.

    Implementation detail:
    - Normalize decimal separator in ONE pass (',' -> '.').
    - Parse once with to_numeric(errors='coerce').
    - Cast to pandas nullable Float64 to preserve <NA>.
    """
    # 1) Ensure string dtype and trim whitespace
    s = s.astype("string").str.strip()

    # 2) Normalize decimal separator (assumes no thousands separators like "1.234,56")
    #    If thousands separators can occur, add a pre-clean step accordingly.
    normalized = s.str.replace(",", ".", regex=False)

    # 3) Parse and cast
    parsed = pd.to_numeric(normalized, errors="coerce")
    return pd.Series(pd.array(parsed, dtype="Float64"), index=s.index)


def to_int64_nullable(s: pd.Series) -> pd.Series:
    """Convert a Series to pandas' nullable Int64 (not numpy int64), coercing errors to <NA>."""
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def to_datetime_safe(s: pd.Series, fmt: Optional[str] = None) -> pd.Series:
    """Best-effort datetime parse with errors='coerce'.

    If fmt is given, it will be used; otherwise pandas will try to infer.
    """
    return pd.to_datetime(s, format=fmt, errors="coerce")


# --- Generic loader -----------------------------------------------------------


def read_csv_all_str(
    csv_path: Path | str, sep: str = ";", encoding: str = "utf-8"
) -> pd.DataFrame:
    """Read a CSV with all columns as string (safe default)."""
    return pd.read_csv(
        csv_path,
        sep=sep,
        encoding=encoding,
        low_memory=False,
        dtype=str,  # critical: don't let pandas guess wrong dtypes
    )

def to_bool_nullable(s: pd.Series) -> pd.Series:
    """Convert a Series with 'Ja'/'Nein'/NULL to nullable boolean (True/False/<NA>)."""
    s = s.astype("string").str.strip().str.lower()

    mapping = {
        "ja": True,
        "nein": False,
    }
    out = s.map(mapping)
    return pd.Series(pd.array(out, dtype="boolean"), index=s.index)

def make_json_safe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df where Period/Datetime/NA are JSON-safe."""
    out = df.copy()

    # Period columns -> 'YYYY-MM' strings
    for col in out.columns:
        if pd.api.types.is_period_dtype(out[col]):
            out[col] = out[col].astype(str)

    # Datetime (tz-naive) -> ISO strings
    for col in out.select_dtypes(include=["datetime64[ns]"]).columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Datetime (tz-aware) -> ISO strings incl. timezone
    for col in out.select_dtypes(include=["datetimetz"]).columns:
        # Use isoformat to retain timezone offset (e.g., '+00:00')
        out[col] = out[col].dt.strftime("%Y-%m-%d %H:%M:%S%z")

    # Pandas <NA>/NaT -> Python None
    out = out.where(pd.notna(out), None)

    return out

def df_to_records_jsonsafe(df: pd.DataFrame) -> list[dict]:
    """Convenience: make DataFrame JSON-serializable and return records list."""
    return make_json_safe(df).to_dict(orient="records")