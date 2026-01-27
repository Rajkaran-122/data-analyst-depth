"""
Reports API Routes (Production)

Backward-compatible report management with database persistence.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import logging
import json

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.report import Report
from app.models.dataset import Dataset
from app.models.query import Query as QueryModel
from app.models.activity import Activity
from app.api.deps import OptionalUser, CurrentUser
from app.services.cache_service import cache, CacheKeys
from app.config import settings
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
async def list_reports(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    report_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    List all reports for the current user.
    """
    if current_user:
        query = db.query(Report).filter(Report.user_id == current_user.id)
        
        if status_filter:
            query = query.filter(Report.status == status_filter)
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        total = query.count()
        reports = query.order_by(desc(Report.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        # Get summary counts
        completed = db.query(func.count(Report.id)).filter(
            Report.user_id == current_user.id,
            Report.status == "completed"
        ).scalar() or 0
        
        pending = db.query(func.count(Report.id)).filter(
            Report.user_id == current_user.id,
            Report.status == "pending"
        ).scalar() or 0
        
        return {
            "reports": [r.to_dict() for r in reports],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "summary": {
                "completed": completed,
                "pending": pending,
                "failed": total - completed - pending,
            }
        }
    
    # Demo reports
    return {
        "reports": [
            {
                "id": "demo-1",
                "title": "Monthly Sales Analysis",
                "query": "Analyze sales trends for the past month",
                "report_type": "summary",
                "status": "completed",
                "insight_count": 5,
                "created_at": datetime.utcnow().isoformat(),
            },
            {
                "id": "demo-2",
                "title": "Customer Segmentation",
                "query": "Segment customers by purchase behavior",
                "report_type": "detailed",
                "status": "completed",
                "insight_count": 8,
                "created_at": datetime.utcnow().isoformat(),
            },
        ],
        "total": 2,
        "page": 1,
        "per_page": 20,
        "total_pages": 1,
        "summary": {"completed": 2, "pending": 0, "failed": 0},
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def generate_report(
    title: str,
    query: str,
    report_type: str = "summary",
    dataset_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Generate a new report.
    """
    # Validate dataset if provided
    dataset = None
    if dataset_id:
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == current_user.id
        ).first()
        if not dataset:
            raise NotFoundError(
                message="Dataset not found",
                resource_type="dataset",
                resource_id=dataset_id,
            )
    
    # Create report
    report = Report(
        user_id=current_user.id,
        dataset_id=dataset_id,
        title=title,
        query=query,
        report_type=report_type,
        status="pending",
    )
    db.add(report)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="report",
        title=f"Report generation started: {title}",
        status="pending",
        metadata={"report_id": str(report.id)},
    )
    db.add(activity)
    
    db.commit()
    db.refresh(report)
    
    # TODO: Queue background job for AI report generation
    # For now, generate a simple report synchronously
    try:
        # Simulate report generation
        report.status = "completed"
        report.completed_at = datetime.utcnow()
        report.summary = f"Analysis of: {query}"
        report.content = f"""
# {title}

## Summary
This report analyzes: {query}

## Key Findings
1. Data patterns have been identified
2. Trends are showing positive growth
3. Recommendations have been generated

## Insights
- Insight 1: Pattern detected in the data
- Insight 2: Correlation found between variables
- Insight 3: Predictive analysis suggests growth

## Recommendations
- Consider expanding analysis scope
- Monitor trends over longer periods
- Implement suggested improvements
"""
        report.insights = [
            {"type": "trend", "title": "Positive Growth", "description": "Data shows upward trend"},
            {"type": "pattern", "title": "Seasonal Pattern", "description": "Recurring pattern detected"},
            {"type": "alert", "title": "Attention Needed", "description": "Some metrics below threshold"},
        ]
        
        # Update activity
        activity.status = "completed"
        
        db.commit()
        db.refresh(report)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        report.status = "failed"
        activity.status = "failed"
        db.commit()
    
    return {
        "message": "Report generated successfully",
        "report": report.to_dict(),
    }


@router.get("/templates")
async def get_report_templates():
    """
    Get available report templates.
    """
    templates = [
        {
            "id": "summary",
            "name": "Summary Report",
            "description": "Quick overview with key metrics and insights",
            "type": "summary",
            "sample_query": "Summarize the main trends in this data",
        },
        {
            "id": "detailed",
            "name": "Detailed Analysis",
            "description": "Comprehensive analysis with visualizations",
            "type": "detailed",
            "sample_query": "Provide a detailed breakdown of all metrics",
        },
        {
            "id": "comparison",
            "name": "Comparison Report",
            "description": "Compare data across different dimensions",
            "type": "comparison",
            "sample_query": "Compare performance across regions and time periods",
        },
        {
            "id": "forecast",
            "name": "Forecast Report",
            "description": "Predictive analysis with future projections",
            "type": "forecast",
            "sample_query": "Forecast next quarter trends based on historical data",
        },
    ]
    
    return {"templates": templates}


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get report details by ID.
    """
    # Check cache
    cache_key = CacheKeys.report(report_id)
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise NotFoundError(
            message="Report not found",
            resource_type="report",
            resource_id=report_id,
        )
    
    # Check ownership if authenticated
    if current_user and str(report.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = report.to_dict()
    
    # Add dataset name if available
    if report.dataset_id:
        dataset = db.query(Dataset).filter(Dataset.id == report.dataset_id).first()
        if dataset:
            result["dataset_name"] = dataset.name
    
    # Cache for 30 minutes
    cache.set(cache_key, result, settings.cache_ttl_reports)
    
    return result


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Delete a report.
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise NotFoundError(
            message="Report not found",
            resource_type="report",
            resource_id=report_id,
        )
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="delete",
        title=f"Deleted report: {report.title}",
        status="success",
    )
    db.add(activity)
    
    db.delete(report)
    db.commit()
    
    # Invalidate cache
    cache.delete(CacheKeys.report(report_id))
    
    return {"message": "Report deleted successfully"}


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query("json", regex="^(json|markdown|html)$"),
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Export report in different formats.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise NotFoundError(
            message="Report not found",
            resource_type="report",
            resource_id=report_id,
        )
    
    # Check ownership if authenticated
    if current_user and str(report.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if format == "json":
        content = json.dumps(report.to_dict(), indent=2, default=str)
        mime_type = "application/json"
        extension = "json"
    elif format == "markdown":
        content = report.content or f"# {report.title}\n\n{report.summary or 'No content available'}"
        mime_type = "text/markdown"
        extension = "md"
    else:  # html
        md_content = report.content or report.summary or "No content available"
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #8B5CF6; }}
        .insight {{ background: #F3F4F6; padding: 10px; margin: 10px 0; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <p><em>Generated: {report.created_at}</em></p>
    <div>{md_content}</div>
</body>
</html>
"""
        mime_type = "text/html"
        extension = "html"
    
    filename = f"{report.title.replace(' ', '_')}_{report_id[:8]}.{extension}"
    
    return {
        "format": format,
        "content": content,
        "filename": filename,
        "mime_type": mime_type,
    }
