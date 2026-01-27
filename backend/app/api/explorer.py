"""
Explorer API Routes (Production)

Data exploration and querying using DuckDB.
"""

from typing import List, Optional, Dict, Any
import logging
import duckdb
import pandas as pd
import os

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.dataset import Dataset
from app.models.query import Query as QueryModel
from app.api.deps import OptionalUser, CurrentUser
from app.core.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/explorer", tags=["Explorer"])


class QueryRequest(BaseModel):
    dataset_id: str
    query: str
    limit: int = 100


class QueryResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    execution_time_ms: float
    row_count: int
    message: Optional[str] = None


@router.post("/query", response_model=QueryResponse)
async def query_dataset(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Execute a SQL query on a dataset using DuckDB.
    """
    import time
    start_time = time.time()
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise NotFoundError(
            message="Dataset not found",
            resource_type="dataset",
            resource_id=request.dataset_id,
        )
    
    # Check ownership/access
    if current_user and str(dataset.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(dataset.file_path):
        raise NotFoundError(
            message="Dataset file not found on disk",
            resource_type="file",
            resource_id=dataset.file_path,
        )
    
    # Initialize DuckDB
    try:
        con = duckdb.connect(database=":memory:")
        
        # Load data based on file type
        if dataset.file_type == "csv":
            con.execute(f"CREATE TABLE data AS SELECT * FROM read_csv_auto('{dataset.file_path}')")
        elif dataset.file_type == "json":
            con.execute(f"CREATE TABLE data AS SELECT * FROM read_json_auto('{dataset.file_path}')")
        elif dataset.file_type in ["xlsx", "xls"]:
            # DuckDB generic excel support via pandas
            df = pd.read_excel(dataset.file_path)
            con.register("data", df)
        else:
            raise BadRequestError(message=f"Unsupported file type: {dataset.file_type}")
        
        # Sanitize query (basic prevention)
        query = request.query.strip().rstrip(";")
        if not query.lower().startswith("select"):
            raise BadRequestError(message="Only SELECT queries are allowed")
            
        # Replace table name aliases if user used "dataset" or "table"
        # We always name the table "data"
        # But advanced users might write "SELECT * FROM data"
        # If they write "SELECT * FROM my_file.csv", that won't work easily.
        # We encourage "SELECT * FROM data"
        
        # Execute query
        # Add limit if not present
        if "limit" not in query.lower():
            query += f" LIMIT {request.limit}"
            
        result_df = con.execute(query).df()
        
        # Convert to response format
        columns = list(result_df.columns)
        # Handle nan/inf for JSON serialization
        result_df = result_df.fillna("") 
        rows = result_df.values.tolist()
        
        execution_time = (time.time() - start_time) * 1000
        
        # Log query if authenticated
        if current_user:
            query_log = QueryModel(
                user_id=current_user.id,
                dataset_id=dataset.id,
                query_text=query,
                status="completed",
                execution_time_ms=int(execution_time),
                source="explorer",
            )
            db.add(query_log)
            db.commit()
        
        return {
            "columns": columns,
            "rows": rows,
            "execution_time_ms": execution_time,
            "row_count": len(rows),
        }
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise BadRequestError(message=f"Query execution failed: {str(e)}")
    finally:
        if 'con' in locals():
            con.close()


@router.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries for learning SQL."""
    return {
        "samples": [
            {
                "name": "Select All",
                "query": "SELECT * FROM data LIMIT 10",
                "description": "View the first 10 rows"
            },
            {
                "name": "Count Rows",
                "query": "SELECT COUNT(*) as total_rows FROM data",
                "description": "Count total records"
            },
            {
                "name": "Filter by Condition",
                "query": "SELECT * FROM data WHERE column_name > 100",
                "description": "Filter rows matching a condition"
            },
            {
                "name": "Group and Aggregate",
                "query": "SELECT category, COUNT(*) as count, AVG(value) as avg_val FROM data GROUP BY category",
                "description": "Group data and calculate statistics"
            }
        ]
    }
