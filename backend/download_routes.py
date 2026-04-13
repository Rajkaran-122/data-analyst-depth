"""
Download API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Downloading raw uploaded datasets
- Downloading cleaned datasets
- Downloading filtered datasets (filters supplied in request body)
- Downloading model-ready datasets
- Downloading AI analysis results as CSV
"""

from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore

from auth import get_current_user  # type: ignore
from storage import storage  # type: ignore
from data_cleaner import (  # type: ignore
    DataCleaner,
    FilterSpec,
    dataframe_to_csv_bytes,
    dataframe_to_json_bytes,
    dataframe_to_xlsx_bytes,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["downloads"])

cleaner = DataCleaner()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class FilterItem(BaseModel):
    column: str
    operator: str = "eq"  # eq, neq, contains, gt, gte, lt, lte, isnull, notnull, in
    value: Optional[Any] = None


class FilteredDownloadRequest(BaseModel):
    filters: List[FilterItem] = []
    columns: Optional[List[str]] = None  # None = all columns
    format: str = "csv"  # csv | json | xlsx


class AnalysisDownloadRequest(BaseModel):
    chart_data: List[Dict[str, Any]]
    filename: Optional[str] = None
    format: str = "csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_dataset(dataset_id: str, user: Dict[str, Any]) -> Any:
    """Look up the dataset and verify ownership, or raise 404/403."""
    ds = storage.get_dataset(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if ds.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return ds


def _get_dataframe(dataset_id: str) -> pd.DataFrame:
    """Return the full DataFrame for a dataset from the file cache."""
    raw = storage.get_file_content(dataset_id)
    if raw is None:
        raise HTTPException(
            status_code=410,
            detail="Dataset file content is no longer available. Please re-upload.",
        )
    try:
        return pd.read_csv(io.BytesIO(raw))
    except Exception:
        try:
            return pd.read_excel(io.BytesIO(raw))
        except Exception:
            import json as _json
            data = _json.loads(raw.decode("utf-8", errors="ignore"))
            return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])


def _make_filename(base: str, variant: str, fmt: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{base}_{variant}_{ts}.{fmt}"


def _stream_response(data_bytes: bytes, filename: str, fmt: str) -> StreamingResponse:
    mime_map = {
        "csv": "text/csv; charset=utf-8",
        "json": "application/json; charset=utf-8",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return StreamingResponse(
        io.BytesIO(data_bytes),
        media_type=mime_map.get(fmt, "application/octet-stream"),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Row-Count": str(len(data_bytes)),
        },
    )


def _export(df: pd.DataFrame, fmt: str) -> bytes:
    if fmt == "json":
        return dataframe_to_json_bytes(df)
    if fmt == "xlsx":
        return dataframe_to_xlsx_bytes(df)
    return dataframe_to_csv_bytes(df)


def _record_download(dataset_id: str, download_type: str, fmt: str, row_count: int, size_bytes: int):
    """Log download event into storage activity system."""
    storage.record_download(
        dataset_id=dataset_id,
        download_type=download_type,
        fmt=fmt,
        row_count=row_count,
        size_bytes=size_bytes,
    )


from fastapi.concurrency import run_in_threadpool

# ---------------------------------------------------------------------------
# 1) Download RAW
# ---------------------------------------------------------------------------

@router.get("/{dataset_id}/download/raw")
async def download_raw(
    dataset_id: str,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Download the original uploaded file as-is (converted to requested format)."""
    ds = _get_user_dataset(dataset_id, current_user)
    df = await run_in_threadpool(_get_dataframe, dataset_id)
    data = await run_in_threadpool(_export, df, format)
    filename = _make_filename(ds.name, "raw", format)
    _record_download(dataset_id, "raw", format, len(df), len(data))
    logger.info("Raw download: %s (%d rows, %d bytes)", filename, len(df), len(data))
    return _stream_response(data, filename, format)


# ---------------------------------------------------------------------------
# 2) Download CLEANED
# ---------------------------------------------------------------------------

@router.get("/{dataset_id}/download/cleaned")
async def download_cleaned(
    dataset_id: str,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Apply automated cleaning pipeline then download."""
    ds = _get_user_dataset(dataset_id, current_user)
    df = await run_in_threadpool(_get_dataframe, dataset_id)
    cleaned = await run_in_threadpool(cleaner.clean, df)
    data = await run_in_threadpool(_export, cleaned, format)
    filename = _make_filename(ds.name, "cleaned", format)
    _record_download(dataset_id, "cleaned", format, len(cleaned), len(data))
    logger.info("Cleaned download: %s (%d rows, %d bytes)", filename, len(cleaned), len(data))
    return _stream_response(data, filename, format)


# ---------------------------------------------------------------------------
# 3) Download FILTERED
# ---------------------------------------------------------------------------

def _apply_filters_and_cols(df: pd.DataFrame, body: FilteredDownloadRequest) -> pd.DataFrame:
    cleaned = cleaner.clean(df)
    if body.filters:
        specs = [FilterSpec.from_dict(f.dict()) for f in body.filters]
        cleaned = DataCleaner.apply_filters(cleaned, specs)
    if body.columns:
        cleaned = DataCleaner.select_columns(cleaned, body.columns)
    return cleaned

@router.post("/{dataset_id}/download/filtered")
async def download_filtered(
    dataset_id: str,
    body: FilteredDownloadRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Apply cleaning + user-supplied filters then download."""
    ds = _get_user_dataset(dataset_id, current_user)
    df = await run_in_threadpool(_get_dataframe, dataset_id)
    
    cleaned = await run_in_threadpool(_apply_filters_and_cols, df, body)

    fmt = body.format if body.format in ("csv", "json", "xlsx") else "csv"
    data = await run_in_threadpool(_export, cleaned, fmt)
    filename = _make_filename(ds.name, "filtered", fmt)
    _record_download(dataset_id, "filtered", fmt, len(cleaned), len(data))
    logger.info("Filtered download: %s (%d rows, %d bytes)", filename, len(cleaned), len(data))
    return _stream_response(data, filename, fmt)


# ---------------------------------------------------------------------------
# 4) Download MODEL-READY
# ---------------------------------------------------------------------------

def _apply_model_ready(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = cleaner.clean(df)
    return cleaner.make_model_ready(cleaned)

@router.get("/{dataset_id}/download/model-ready")
async def download_model_ready(
    dataset_id: str,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Apply cleaning + ML-ready transforms then download."""
    ds = _get_user_dataset(dataset_id, current_user)
    df = await run_in_threadpool(_get_dataframe, dataset_id)
    
    model_df = await run_in_threadpool(_apply_model_ready, df)
    
    data = await run_in_threadpool(_export, model_df, format)
    filename = _make_filename(ds.name, "model_ready", format)
    _record_download(dataset_id, "model-ready", format, len(model_df), len(data))
    logger.info("Model-ready download: %s (%d rows, %d cols, %d bytes)", filename, len(model_df), len(model_df.columns), len(data))
    return _stream_response(data, filename, format)


# ---------------------------------------------------------------------------
# 5) Download ANALYSIS RESULTS
# ---------------------------------------------------------------------------

@router.post("/analysis/download")
async def download_analysis_results(
    body: AnalysisDownloadRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Convert AI-generated chartData to a downloadable file."""
    if not body.chart_data:
        raise HTTPException(status_code=400, detail="No chart data provided")

    df = pd.DataFrame(body.chart_data)
    fmt = body.format if body.format in ("csv", "json", "xlsx") else "csv"
    data = await run_in_threadpool(_export, df, fmt)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = body.filename or "analysis_results"
    filename = f"{base}_{ts}.{fmt}"


    logger.info("Analysis results download: %s (%d rows, %d bytes)", filename, len(df), len(data))
    return _stream_response(data, filename, fmt)


# ---------------------------------------------------------------------------
# 6) Preview endpoint (cleaned data preview with stats + quality score)
# ---------------------------------------------------------------------------

def _compute_quality_score(df_original: pd.DataFrame, df_cleaned: pd.DataFrame) -> Dict[str, Any]:
    """Compute a 0-100 quality score with per-dimension breakdown."""
    scores = {}

    # Completeness (0-30): % of non-null values after cleaning
    total_cells = df_cleaned.size or 1
    non_null_cells = df_cleaned.notna().sum().sum()
    completeness = round((non_null_cells / total_cells) * 100, 1)
    scores["completeness"] = min(completeness, 100.0)

    # Uniqueness (0-25): inverse of duplicate ratio in original
    dup_ratio = 1 - (len(df_cleaned) / max(len(df_original), 1))
    uniqueness = round((1 - dup_ratio) * 100, 1)
    scores["uniqueness"] = min(uniqueness, 100.0)

    # Consistency (0-25): % of columns with uniform dtype (no mixed types)
    consistent_cols = 0
    for col in df_cleaned.columns:
        if df_cleaned[col].dtype != object:
            consistent_cols += 1
        else:
            # Check if all non-null values can be parsed as one type
            sample = df_cleaned[col].dropna().head(100)
            num_test = pd.to_numeric(sample, errors="coerce")
            if num_test.notna().mean() > 0.9 or num_test.notna().mean() < 0.1:
                consistent_cols += 1
    consistency = round((consistent_cols / max(len(df_cleaned.columns), 1)) * 100, 1)
    scores["consistency"] = min(consistency, 100.0)

    # Validity (0-20): % of rows retained after cleaning
    validity = round((len(df_cleaned) / max(len(df_original), 1)) * 100, 1)
    scores["validity"] = min(validity, 100.0)

    # Weighted overall score
    overall = round(
        scores["completeness"] * 0.30
        + scores["uniqueness"] * 0.25
        + scores["consistency"] * 0.25
        + scores["validity"] * 0.20,
        1,
    )
    scores["overall"] = min(overall, 100.0)

    # Grade label
    if overall >= 90:
        scores["grade"] = "Excellent"
    elif overall >= 75:
        scores["grade"] = "Good"
    elif overall >= 60:
        scores["grade"] = "Fair"
    else:
        scores["grade"] = "Needs Work"

    return scores


def _estimate_sizes(df: pd.DataFrame) -> Dict[str, int]:
    """Estimate export sizes (bytes) for each format without full serialisation."""
    csv_est = int(df.memory_usage(deep=True).sum() * 0.35)     # CSV is ~35% of memory
    json_est = int(csv_est * 1.8)                                # JSON has key overhead
    xlsx_est = int(csv_est * 0.9)                                # XLSX has compression
    return {"csv": csv_est, "json": json_est, "xlsx": xlsx_est}


@router.get("/{dataset_id}/preview/cleaned")
async def preview_cleaned(
    dataset_id: str,
    rows: int = Query(50, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Return a preview of the cleaned dataset with summary statistics, quality score, and size estimates."""
    ds = _get_user_dataset(dataset_id, current_user)
    df = _get_dataframe(dataset_id)
    cleaned = cleaner.clean(df)

    # Build column stats
    columns_info = []
    for col in cleaned.columns:
        null_pct = round(cleaned[col].isnull().mean() * 100, 2)
        col_info: Dict[str, Any] = {
            "name": col,
            "dtype": str(cleaned[col].dtype),
            "null_percentage": null_pct,
            "unique_count": int(cleaned[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(cleaned[col]):
            col_info["min"] = float(cleaned[col].min()) if cleaned[col].notna().any() else None
            col_info["max"] = float(cleaned[col].max()) if cleaned[col].notna().any() else None
            col_info["mean"] = float(cleaned[col].mean()) if cleaned[col].notna().any() else None
        columns_info.append(col_info)

    # Preview rows  (replace NaN with None for JSON)
    preview_df = cleaned.head(rows).where(cleaned.head(rows).notna(), None)

    # Quality score
    quality = _compute_quality_score(df, cleaned)

    # Estimated file sizes
    size_estimates = _estimate_sizes(cleaned)

    return {
        "dataset_id": dataset_id,
        "name": ds.name,
        "original_rows": len(df),
        "cleaned_rows": len(cleaned),
        "rows_removed": len(df) - len(cleaned),
        "column_count": len(cleaned.columns),
        "columns": columns_info,
        "preview": preview_df.to_dict(orient="records"),
        "quality_score": quality,
        "estimated_sizes": size_estimates,
    }


# ---------------------------------------------------------------------------
# 7) Download History
# ---------------------------------------------------------------------------

@router.get("/downloads/history")
async def download_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Return the user's recent download activity."""
    stats = storage.get_download_stats()
    return {
        "total_downloads": stats["total_downloads"],
        "recent": stats["recent_downloads"],
    }
