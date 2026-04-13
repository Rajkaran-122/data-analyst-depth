"""
Data Cleaning & Transformation Pipeline for Data Analyst Depth.

Provides:
- DataCleaner: standardised cleaning (dedup, type coercion, null handling)
- Model-ready transforms (imputation, encoding, normalisation)
- CSV / JSON / XLSX export helpers with streaming support
"""

from __future__ import annotations

import io
import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd  # type: ignore
import numpy as np   # type: ignore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Filter specification
# ---------------------------------------------------------------------------

class FilterSpec:
    """Lightweight filter descriptor."""

    def __init__(
        self,
        column: str,
        operator: str,          # eq, neq, contains, gt, gte, lt, lte, isnull, notnull, in
        value: Any = None,
    ):
        self.column = column
        self.operator = operator
        self.value = value

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilterSpec":
        return cls(
            column=d.get("column", ""),
            operator=d.get("operator", "eq"),
            value=d.get("value"),
        )


# ---------------------------------------------------------------------------
# DataCleaner
# ---------------------------------------------------------------------------

class DataCleaner:
    """
    Standardised data-cleaning pipeline.

    Stage 1 – Remove fully-duplicate rows
    Stage 2 – Strip whitespace from string/object columns
    Stage 3 – Coerce numeric-looking columns to numeric dtype
    Stage 4 – Parse date-looking columns to datetime
    Stage 5 – Drop rows where ALL values are null
    Stage 6 – Standardise column names (lowercase, underscores)
    """

    # ------------------------------------------------------------------ clean
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned copy of *df*."""
        out = df.copy()
        row_before = len(out)

        # Stage 1 – dedup
        out = out.drop_duplicates()

        # Stage 2 – strip whitespace on object columns
        for col in out.select_dtypes(include=["object"]).columns:
            out[col] = out[col].astype(str).str.strip()
            # Restore actual NaN (pandas converts NaN -> "nan" via astype(str))
            out.loc[out[col] == "nan", col] = np.nan

        # Stage 3 – coerce numeric
        for col in out.columns:
            if out[col].dtype == object:
                converted = pd.to_numeric(out[col], errors="coerce")
                non_null_ratio = converted.notna().sum() / max(out[col].notna().sum(), 1)
                if non_null_ratio > 0.6:
                    out[col] = converted

        # Stage 4 – parse dates
        for col in out.columns:
            if out[col].dtype == object:
                try:
                    parsed = pd.to_datetime(out[col], errors="coerce")
                    non_null_ratio = parsed.notna().sum() / max(out[col].notna().sum(), 1)
                    if non_null_ratio > 0.6:
                        out[col] = parsed
                except Exception:
                    pass

        # Stage 5 – drop all-null rows
        out = out.dropna(how="all")

        # Stage 6 – standardise column names
        out.columns = [
            str(c).strip().lower().replace(" ", "_").replace("-", "_")
            for c in out.columns
        ]

        rows_removed = row_before - len(out)
        logger.info(
            "Cleaned dataset: %d → %d rows (%d removed)",
            row_before, len(out), rows_removed,
        )
        return out

    # ---------------------------------------------------------- model-ready
    def make_model_ready(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Additional transforms for ML readiness on an already-cleaned frame.

        1. Impute remaining nulls  (median for numeric, mode for categorical)
        2. One-hot encode categoricals with ≤ 10 unique values
        3. Label-encode categoricals with > 10 unique values
        4. Min-max normalise numeric columns to [0, 1]
        """
        out = df.copy()

        # --- imputation ---
        for col in out.columns:
            if out[col].isnull().sum() == 0:
                continue
            if pd.api.types.is_numeric_dtype(out[col]):
                out[col] = out[col].fillna(out[col].median())
            else:
                mode_val = out[col].mode()
                fill = mode_val.iloc[0] if len(mode_val) > 0 else "unknown"
                out[col] = out[col].fillna(fill)

        # --- encoding ---
        cat_cols = out.select_dtypes(include=["object", "category"]).columns.tolist()
        for col in cat_cols:
            nunique = out[col].nunique()
            if nunique <= 10:
                dummies = pd.get_dummies(out[col], prefix=col, drop_first=True)
                dummies = dummies.astype(int)
                out = pd.concat([out.drop(columns=[col]), dummies], axis=1)
            else:
                labels, _ = pd.factorize(out[col])
                out[col] = labels

        # --- normalisation ---
        num_cols = out.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            cmin = out[col].min()
            cmax = out[col].max()
            if cmax - cmin > 0:
                out[col] = (out[col] - cmin) / (cmax - cmin)
            else:
                out[col] = 0.0

        # Drop datetime columns (not useful for ML in raw form)
        dt_cols = out.select_dtypes(include=["datetime", "datetimetz"]).columns
        if len(dt_cols) > 0:
            out = out.drop(columns=dt_cols)

        logger.info("Model-ready dataset: %d rows × %d cols", len(out), len(out.columns))
        return out

    # ------------------------------------------------------- apply filters
    @staticmethod
    def apply_filters(df: pd.DataFrame, filters: List[FilterSpec]) -> pd.DataFrame:
        """Apply a list of column-level filters and return the matching rows."""
        out = df.copy()
        for f in filters:
            if f.column not in out.columns:
                continue
            col = out[f.column]
            if f.operator == "eq":
                out = out[col.astype(str) == str(f.value)]
            elif f.operator == "neq":
                out = out[col.astype(str) != str(f.value)]
            elif f.operator == "contains":
                out = out[col.astype(str).str.contains(str(f.value), case=False, na=False)]
            elif f.operator == "gt":
                numeric = pd.to_numeric(col, errors="coerce")
                out = out[numeric > float(f.value)]
            elif f.operator == "gte":
                numeric = pd.to_numeric(col, errors="coerce")
                out = out[numeric >= float(f.value)]
            elif f.operator == "lt":
                numeric = pd.to_numeric(col, errors="coerce")
                out = out[numeric < float(f.value)]
            elif f.operator == "lte":
                numeric = pd.to_numeric(col, errors="coerce")
                out = out[numeric <= float(f.value)]
            elif f.operator == "isnull":
                out = out[col.isnull()]
            elif f.operator == "notnull":
                out = out[col.notna()]
            elif f.operator == "in":
                vals = f.value if isinstance(f.value, list) else str(f.value).split(",")
                vals = [v.strip() for v in vals]
                out = out[col.astype(str).isin(vals)]
        return out

    # ------------------------------------------------------- select columns
    @staticmethod
    def select_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Select only the requested columns from *df*."""
        valid = [c for c in columns if c in df.columns]
        return df[valid] if valid else df


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialise *df* to CSV bytes with UTF-8 BOM for Excel compatibility."""
    buf = io.BytesIO()
    buf.write(b"\xef\xbb\xbf")  # UTF-8 BOM
    df.to_csv(buf, index=False, encoding="utf-8")
    buf.seek(0)
    return buf.read()


def dataframe_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Serialise *df* to JSON bytes (array-of-objects)."""
    # Handle NaN → null, datetime → ISO string
    return df.to_json(orient="records", date_format="iso", default_handler=str).encode("utf-8")


def dataframe_to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    """Serialise *df* to XLSX bytes via openpyxl. Strips timezones to prevent crash."""
    buf = io.BytesIO()
    
    # openpyxl cannot handle timezone-aware datetimes
    export_df = df.copy()
    for col in export_df.select_dtypes(include=['datetimetz']).columns:
        export_df[col] = export_df[col].dt.tz_localize(None)
        
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Data")
    buf.seek(0)
    return buf.read()
