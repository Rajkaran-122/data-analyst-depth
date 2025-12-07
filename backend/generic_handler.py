
import os
import io
import base64
import pandas as pd
import matplotlib
# Use Agg backend to avoid GUI issues
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def _encode_plot_to_data_uri() -> str:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def _offline_handle_generic_csv() -> Dict[str, Any]:
    """Fallback handler for generic CSV files when LLM is not configured."""
    try:
        # Debugging: Print current directory to ensure we are where we think we are
        # print(f"DEBUG: Current generic handler cwd: {os.getcwd()}")
        
        if not os.path.exists("data.csv"):
            return {
                "summary": "No data file found to analyze.",
                "data": {},
                "visualizations": [],
                "status": "failed",
                "error": "data.csv missing in temp directory"
            }
        
        df = pd.read_csv("data.csv")
        
        # Basic stats
        row_count = len(df)
        col_count = len(df.columns)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Convert describe to dict and handle potential NaNs for JSON serialization
        summary_stats = df.describe().fillna(0).to_dict()
        
        visualizations = []
        
        # Create a histogram for the first numeric column
        if numeric_cols:
            plt.figure(figsize=(6, 4))
            col = numeric_cols[0]
            # Drop NA for plotting
            series = df[col].dropna()
            if not series.empty:
                plt.hist(series, bins=15, color='teal', edgecolor='black', alpha=0.7)
                plt.title(f'Distribution of {col}')
                plt.xlabel(col)
                plt.ylabel('Frequency')
                plt.grid(axis='y', alpha=0.2)
                plt.tight_layout()
                visualizations.append(_encode_plot_to_data_uri())
            
        # Create a bar chart for the first categorical column (top 10)
        if object_cols:
            plt.figure(figsize=(6, 4))
            col = object_cols[0]
            counts = df[col].value_counts().head(10)
            if not counts.empty:
                plt.bar(counts.index.astype(str), counts.values, color='purple', alpha=0.7)
                plt.title(f'Top 10 {col}')
                plt.xlabel(col)
                plt.ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.2)
                plt.tight_layout()
                visualizations.append(_encode_plot_to_data_uri())
            
        return {
            "summary": f"Analyzed dataset with {row_count} rows and {col_count} columns. Found {len(numeric_cols)} numeric and {len(object_cols)} categorical columns.",
            "data": {
                "rows": row_count,
                "columns": list(df.columns),
                "numeric_columns": numeric_cols,
                "categorical_columns": object_cols,
                "summary_statistics": summary_stats
            },
            "visualizations": visualizations,
            "insights": [
                f"Dataset contains {row_count} records.",
                f"Numeric columns: {', '.join(numeric_cols[:5])}",
                f"Categorical columns: {', '.join(object_cols[:5])}"
            ],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Generic CSV handler failed: {e}")
        # Return a partial success or specific error so we know it crashed here
        return {
            "summary": "Failed to analyze CSV file.",
            "data": {},
            "visualizations": [],
            "status": "error",
            "error": str(e)
        }
