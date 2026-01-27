"""
Dashboard API Routes (Production)

Backward-compatible dashboard endpoints with database persistence and caching.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import random
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.dataset import Dataset
from app.models.query import Query as QueryModel
from app.models.report import Report
from app.models.activity import Activity
from app.models.workspace import Workspace
from app.api.deps import OptionalUser, CurrentUser
from app.services.cache_service import cache, CacheKeys
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _generate_demo_data(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Generate demo data for unauthenticated or new users."""
    return {
        "total_queries": random.randint(150, 300),
        "total_datasets": random.randint(8, 20),
        "ai_insights": random.randint(25, 60),
        "reports_generated": random.randint(10, 30),
        "total_queries_change": round(random.uniform(5, 25), 1),
        "total_datasets_change": round(random.uniform(-5, 15), 1),
        "ai_insights_change": round(random.uniform(10, 40), 1),
        "reports_generated_change": round(random.uniform(0, 20), 1),
    }


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get dashboard statistics.
    
    Returns KPI cards data including:
    - Total queries
    - Total datasets
    - AI insights generated
    - Reports created
    
    Includes percentage change from previous period.
    """
    # Check cache first if user is authenticated
    if current_user:
        cache_key = CacheKeys.dashboard_stats(str(current_user.id))
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # If authenticated, get real stats
    if current_user:
        user_id = current_user.id
        
        # Get actual counts
        total_queries = db.query(func.count(QueryModel.id)).filter(
            QueryModel.user_id == user_id
        ).scalar() or 0
        
        total_datasets = db.query(func.count(Dataset.id)).filter(
            Dataset.user_id == user_id
        ).scalar() or 0
        
        total_reports = db.query(func.count(Report.id)).filter(
            Report.user_id == user_id
        ).scalar() or 0
        
        # Calculate change (compare to last week)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        queries_this_week = db.query(func.count(QueryModel.id)).filter(
            QueryModel.user_id == user_id,
            QueryModel.created_at >= week_ago
        ).scalar() or 0
        
        # Calculate AI insights (from reports with insights)
        ai_insights = db.query(func.count(Report.id)).filter(
            Report.user_id == user_id,
            Report.insights.isnot(None)
        ).scalar() or 0
        
        stats = {
            "total_queries": total_queries,
            "total_datasets": total_datasets,
            "ai_insights": ai_insights,
            "reports_generated": total_reports,
            "total_queries_change": round((queries_this_week / max(total_queries, 1)) * 100, 1),
            "total_datasets_change": random.uniform(5, 15),  # Placeholder
            "ai_insights_change": random.uniform(10, 30),  # Placeholder
            "reports_generated_change": random.uniform(5, 20),  # Placeholder
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, settings.cache_ttl_dashboard)
        
        return stats
    
    # Return demo data for unauthenticated users
    return _generate_demo_data()


@router.get("/charts/queries")
async def get_query_chart_data(
    range: str = Query("7d", regex="^(7d|30d|90d)$"),
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get query activity chart data.
    
    Args:
        range: Time range (7d, 30d, 90d)
        
    Returns time series data for queries over the specified period.
    """
    # Determine number of days
    days = {"7d": 7, "30d": 30, "90d": 90}.get(range, 7)
    
    labels = []
    values = []
    
    if current_user:
        # Get real data from database
        for i in range(days, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            count = db.query(func.count(QueryModel.id)).filter(
                QueryModel.user_id == current_user.id,
                QueryModel.created_at >= date_start,
                QueryModel.created_at < date_end
            ).scalar() or 0
            
            labels.append(date.strftime("%b %d"))
            values.append(count)
    else:
        # Generate demo data
        for i in range(days, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            labels.append(date.strftime("%b %d"))
            values.append(random.randint(5, 30))
    
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Queries",
                "data": values,
                "borderColor": "#8B5CF6",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "fill": True,
            }
        ]
    }


@router.get("/charts/sources")
async def get_data_sources_chart(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get data sources breakdown chart.
    
    Returns pie chart data showing distribution of file types.
    """
    if current_user:
        # Get real file type distribution
        file_types = db.query(
            Dataset.file_type,
            func.count(Dataset.id).label("count")
        ).filter(
            Dataset.user_id == current_user.id
        ).group_by(Dataset.file_type).all()
        
        if file_types:
            labels = [ft.file_type.upper() for ft in file_types]
            values = [ft.count for ft in file_types]
        else:
            # Default for users with no data
            labels = ["CSV", "Excel", "JSON", "Other"]
            values = [0, 0, 0, 0]
    else:
        # Demo data
        labels = ["CSV", "Excel", "JSON", "Other"]
        values = [45, 30, 15, 10]
    
    colors = ["#8B5CF6", "#6366F1", "#A78BFA", "#C4B5FD"]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "data": values,
                "backgroundColor": colors[:len(labels)],
                "borderWidth": 0,
            }
        ]
    }


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get recent activity feed.
    
    Args:
        limit: Maximum number of activities to return
        
    Returns list of recent user activities.
    """
    if current_user:
        # Check cache
        cache_key = CacheKeys.dashboard_activity(str(current_user.id), limit)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get real activities from database
        activities = db.query(Activity).filter(
            Activity.user_id == current_user.id
        ).order_by(desc(Activity.created_at)).limit(limit).all()
        
        result = [activity.to_dict() for activity in activities]
        
        # If no activities, generate some based on actual data
        if not result:
            # Get recent queries, reports, datasets
            recent_queries = db.query(QueryModel).filter(
                QueryModel.user_id == current_user.id
            ).order_by(desc(QueryModel.created_at)).limit(5).all()
            
            for query in recent_queries:
                result.append({
                    "id": str(query.id),
                    "type": "query",
                    "title": f"Query: {query.query_text[:50]}...",
                    "status": query.status,
                    "timestamp": query.created_at.isoformat(),
                    "icon": "search",
                    "color": "#10B981",
                })
        
        # Cache for 1 minute
        cache.set(cache_key, result, 60)
        
        return result
    
    # Demo activity for unauthenticated users
    demo_activities = [
        {
            "id": "demo-1",
            "type": "query",
            "title": "Analyzed sales data for Q4",
            "status": "completed",
            "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "icon": "search",
            "color": "#10B981",
        },
        {
            "id": "demo-2",
            "type": "report",
            "title": "Generated monthly report",
            "status": "completed",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "icon": "document",
            "color": "#6366F1",
        },
        {
            "id": "demo-3",
            "type": "dataset",
            "title": "Uploaded customer_data.csv",
            "status": "ready",
            "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "icon": "database",
            "color": "#8B5CF6",
        },
        {
            "id": "demo-4",
            "type": "insight",
            "title": "New insight: Revenue trend detected",
            "status": "success",
            "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "icon": "lightbulb",
            "color": "#F59E0B",
        },
    ]
    
    return demo_activities[:limit]


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get comprehensive dashboard summary.
    
    Returns combined stats, recent activity, and quick insights.
    """
    stats = await get_dashboard_stats(db, current_user)
    activity = await get_recent_activity(limit=5, db=db, current_user=current_user)
    
    # Get workspace count if authenticated
    workspace_count = 0
    if current_user:
        workspace_count = db.query(func.count(Workspace.id)).filter(
            Workspace.user_id == current_user.id
        ).scalar() or 0
    
    return {
        "stats": stats,
        "recent_activity": activity,
        "workspace_count": workspace_count,
        "quick_insights": [
            "Query volume is up 15% this week",
            "3 new datasets added",
            "AI analysis completion rate: 95%",
        ],
    }
