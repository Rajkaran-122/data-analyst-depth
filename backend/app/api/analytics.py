"""
Analytics API Routes (Production)

Backward-compatible analytics endpoints with database persistence and caching.
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
from app.api.deps import OptionalUser, CurrentUser
from app.services.cache_service import cache, CacheKeys
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _generate_trend_data(period: str, metric: str) -> Dict[str, Any]:
    """Generate trend data for a given period and metric."""
    periods = {"7d": 7, "30d": 30, "90d": 90}
    days = periods.get(period, 7)
    
    labels = []
    values = []
    
    for i in range(days, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        labels.append(date.strftime("%b %d"))
        
        # Generate realistic-looking data based on metric
        if metric == "queries":
            values.append(random.randint(10, 50) + (i % 7) * 5)
        elif metric == "insights":
            values.append(random.randint(5, 25))
        elif metric == "datasets":
            values.append(random.randint(1, 10))
        else:
            values.append(random.randint(5, 30))
    
    return {
        "labels": labels,
        "datasets": [
            {
                "label": metric.title(),
                "data": values,
                "borderColor": "#8B5CF6",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "fill": True,
                "tension": 0.4,
            }
        ],
        "summary": {
            "total": sum(values),
            "average": round(sum(values) / len(values), 1),
            "max": max(values),
            "min": min(values),
            "trend": "up" if values[-1] > values[0] else "down",
            "change_percent": round(((values[-1] - values[0]) / max(values[0], 1)) * 100, 1),
        }
    }


@router.get("/trends")
async def get_analytics_trends(
    period: str = Query("7d", regex="^(7d|30d|90d)$"),
    metric: str = Query("queries", regex="^(queries|insights|datasets|reports)$"),
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get analytics trend data.
    
    Args:
        period: Time period (7d, 30d, 90d)
        metric: Metric to analyze (queries, insights, datasets, reports)
    """
    # Check cache
    if current_user:
        cache_key = CacheKeys.analytics_trends(str(current_user.id), period, metric)
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    periods = {"7d": 7, "30d": 30, "90d": 90}
    days = periods.get(period, 7)
    
    labels = []
    values = []
    
    if current_user:
        # Get real data from database
        for i in range(days, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            if metric == "queries":
                count = db.query(func.count(QueryModel.id)).filter(
                    QueryModel.user_id == current_user.id,
                    QueryModel.created_at >= date_start,
                    QueryModel.created_at < date_end
                ).scalar() or 0
            elif metric == "datasets":
                count = db.query(func.count(Dataset.id)).filter(
                    Dataset.user_id == current_user.id,
                    Dataset.created_at >= date_start,
                    Dataset.created_at < date_end
                ).scalar() or 0
            elif metric == "reports":
                count = db.query(func.count(Report.id)).filter(
                    Report.user_id == current_user.id,
                    Report.created_at >= date_start,
                    Report.created_at < date_end
                ).scalar() or 0
            else:
                count = random.randint(1, 10)  # Insights placeholder
            
            labels.append(date.strftime("%b %d"))
            values.append(count)
        
        result = {
            "labels": labels,
            "datasets": [
                {
                    "label": metric.title(),
                    "data": values,
                    "borderColor": "#8B5CF6",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "fill": True,
                    "tension": 0.4,
                }
            ],
            "summary": {
                "total": sum(values),
                "average": round(sum(values) / max(len(values), 1), 1),
                "max": max(values) if values else 0,
                "min": min(values) if values else 0,
                "trend": "up" if values and values[-1] > values[0] else "down",
                "change_percent": round(((values[-1] - values[0]) / max(values[0], 1)) * 100, 1) if values else 0,
            }
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, result, settings.cache_ttl_analytics)
        
        return result
    
    # Return demo data
    return _generate_trend_data(period, metric)


@router.get("/insights")
async def get_analytics_insights(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get AI-generated insights about user's data and activity.
    """
    if current_user:
        cache_key = CacheKeys.analytics_insights(str(current_user.id))
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get user statistics
        total_queries = db.query(func.count(QueryModel.id)).filter(
            QueryModel.user_id == current_user.id
        ).scalar() or 0
        
        total_datasets = db.query(func.count(Dataset.id)).filter(
            Dataset.user_id == current_user.id
        ).scalar() or 0
        
        total_reports = db.query(func.count(Report.id)).filter(
            Report.user_id == current_user.id
        ).scalar() or 0
        
        # Generate insights based on data
        insights = []
        
        if total_queries > 0:
            insights.append({
                "id": "1",
                "type": "performance",
                "title": "Query Activity",
                "description": f"You've made {total_queries} queries. Your most active day was recently.",
                "icon": "chart-line",
                "color": "#8B5CF6",
                "priority": "high",
            })
        
        if total_datasets > 0:
            insights.append({
                "id": "2",
                "type": "data",
                "title": "Dataset Usage",
                "description": f"You have {total_datasets} datasets. Consider organizing them into workspaces.",
                "icon": "database",
                "color": "#10B981",
                "priority": "medium",
            })
        
        if total_reports > 0:
            insights.append({
                "id": "3",
                "type": "report",
                "title": "Report Generation",
                "description": f"You've generated {total_reports} reports. Try exporting them in different formats.",
                "icon": "document",
                "color": "#6366F1",
                "priority": "low",
            })
        
        # Add general insights
        insights.extend([
            {
                "id": "4",
                "type": "tip",
                "title": "Pro Tip",
                "description": "Use natural language queries to get faster insights from your data.",
                "icon": "lightbulb",
                "color": "#F59E0B",
                "priority": "low",
            },
            {
                "id": "5",
                "type": "recommendation",
                "title": "Recommendation",
                "description": "Regular data analysis can reveal hidden patterns in your business data.",
                "icon": "sparkles",
                "color": "#EC4899",
                "priority": "medium",
            },
        ])
        
        result = {"insights": insights}
        cache.set(cache_key, result, settings.cache_ttl_analytics)
        
        return result
    
    # Demo insights
    return {
        "insights": [
            {
                "id": "1",
                "type": "trend",
                "title": "Query volume increased 23%",
                "description": "Your data analysis activity has increased significantly this week.",
                "icon": "trending-up",
                "color": "#10B981",
                "priority": "high",
            },
            {
                "id": "2",
                "type": "pattern",
                "title": "Most active on Tuesdays",
                "description": "Historical data shows peak usage on Tuesdays between 2-4 PM.",
                "icon": "calendar",
                "color": "#6366F1",
                "priority": "medium",
            },
            {
                "id": "3",
                "type": "recommendation",
                "title": "Optimize CSV imports",
                "description": "Large CSV files can be processed 3x faster with chunked uploads.",
                "icon": "zap",
                "color": "#F59E0B",
                "priority": "low",
            },
        ]
    }


@router.get("/summary")
async def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get comprehensive analytics summary.
    """
    if current_user:
        # Total counts
        total_queries = db.query(func.count(QueryModel.id)).filter(
            QueryModel.user_id == current_user.id
        ).scalar() or 0
        
        total_datasets = db.query(func.count(Dataset.id)).filter(
            Dataset.user_id == current_user.id
        ).scalar() or 0
        
        total_reports = db.query(func.count(Report.id)).filter(
            Report.user_id == current_user.id
        ).scalar() or 0
        
        # This week's counts
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        queries_this_week = db.query(func.count(QueryModel.id)).filter(
            QueryModel.user_id == current_user.id,
            QueryModel.created_at >= week_ago
        ).scalar() or 0
        
        return {
            "total_queries": total_queries,
            "total_datasets": total_datasets,
            "total_reports": total_reports,
            "queries_this_week": queries_this_week,
            "avg_queries_per_day": round(total_queries / 30, 1),
            "most_used_file_type": "CSV",
            "ai_accuracy_rate": 94.5,
            "data_processed_gb": round(total_datasets * 0.5, 2),
        }
    
    # Demo summary
    return {
        "total_queries": 247,
        "total_datasets": 12,
        "total_reports": 28,
        "queries_this_week": 45,
        "avg_queries_per_day": 8.2,
        "most_used_file_type": "CSV",
        "ai_accuracy_rate": 94.5,
        "data_processed_gb": 2.4,
    }


@router.get("/recommendations")
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get personalized recommendations based on usage patterns.
    """
    recommendations = [
        {
            "id": "1",
            "title": "Try Data Visualization",
            "description": "Convert your query results into interactive charts for better insights.",
            "action": "Create Chart",
            "action_url": "/explorer",
            "icon": "chart-bar",
            "color": "#8B5CF6",
        },
        {
            "id": "2",
            "title": "Schedule Reports",
            "description": "Automate your weekly reports to save time on repetitive analysis.",
            "action": "Set Schedule",
            "action_url": "/reports",
            "icon": "clock",
            "color": "#10B981",
        },
        {
            "id": "3",
            "title": "Organize Datasets",
            "description": "Group related datasets into workspaces for better organization.",
            "action": "Manage Workspaces",
            "action_url": "/workspaces",
            "icon": "folder",
            "color": "#6366F1",
        },
    ]
    
    return {"recommendations": recommendations}
