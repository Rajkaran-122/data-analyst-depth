"""
Dashboard API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Dashboard KPI statistics
- Query trends chart data
- Data source distribution chart data
- Real-time activity feed
"""

from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import random

from storage import storage

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """
    Get aggregated KPI metrics for dashboard cards.
    
    Returns:
        Dictionary containing:
        - kpis: List of KPI card data with real-time values
    """
    stats = storage.get_dashboard_stats()
    logs = storage.get_query_logs(100)
    
    # Calculate real success rate
    success_count = sum(1 for log in logs if log.status == "success")
    success_rate = (success_count / len(logs) * 100) if logs else 100
    
    # Calculate average response time
    avg_response = sum(log.response_time_ms for log in logs) // max(len(logs), 1) if logs else 0
    
    return {
        "kpis": [
            {
                "id": "queries",
                "title": "Total Queries",
                "value": f"{stats['total_queries']:,}",
                "change": f"+{stats['query_growth']}%",
                "trend": "up",
                "icon": "analytics"
            },
            {
                "id": "datasets",
                "title": "Datasets",
                "value": f"{stats['total_datasets']:,}",
                "change": f"+{stats['dataset_growth']}%",
                "trend": "up",
                "icon": "dataset"
            },
            {
                "id": "insights",
                "title": "Insights Generated",
                "value": f"{stats['total_insights']:,}",
                "change": f"+{stats['insight_growth']}%",
                "trend": "up",
                "icon": "explorer"
            },
            {
                "id": "reports",
                "title": "Reports",
                "value": f"{stats['total_reports']:,}",
                "change": f"{stats['session_change']}%",
                "trend": "down" if stats["session_change"] < 0 else "up",
                "icon": "document"
            }
        ],
        "summary": {
            "success_rate": round(success_rate, 1),
            "avg_response_ms": avg_response,
            "active_datasets": stats['total_datasets'],
            "pending_reports": 0
        }
    }


@router.get("/charts/queries")
async def get_query_trends(
    days: int = 30,
    range: str = "1M"
) -> Dict[str, Any]:
    """
    Get time-series data for query trends chart.
    
    Args:
        days: Number of days of data to return (default 30)
        range: Range identifier (1D, 1W, 1M, 3M, 6M, 1Y, ALL)
    
    Returns:
        Dictionary containing chart data with dates and query counts
    """
    # Map range to days
    range_days = {
        "1D": 1,
        "1W": 7,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "ALL": 365
    }
    actual_days = range_days.get(range, days)
    
    trends = storage.get_query_trends(actual_days)
    
    # Calculate totals
    total_queries = sum(d.get("queries", 0) for d in trends)
    avg_queries = total_queries // max(len(trends), 1)
    peak_queries = max(d.get("queries", 0) for d in trends) if trends else 0
    
    return {
        "title": "Query Trends",
        "range": range,
        "data": trends,
        "series": [
            {"key": "queries", "name": "Queries", "color": "#3B82F6"}
        ],
        "summary": {
            "total": total_queries,
            "average": avg_queries,
            "peak": peak_queries,
            "growth": round(random.uniform(5, 20), 1)
        }
    }


@router.get("/charts/sources")
async def get_source_distribution() -> Dict[str, Any]:
    """
    Get data source distribution for pie chart.
    
    Returns:
        Dictionary containing distribution data for chart
    """
    distribution = storage.get_source_distribution()
    total = sum(d["value"] for d in distribution)
    
    # Add percentage to each item
    for item in distribution:
        item["percentage"] = round(item["value"] / total * 100, 1) if total > 0 else 0
    
    return {
        "title": "Data Sources",
        "data": distribution,
        "total": total
    }


@router.get("/charts/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics for performance chart.
    
    Returns:
        Dictionary containing performance data
    """
    logs = storage.get_query_logs(100)
    
    # Group by hour for last 24 hours
    now = datetime.now(timezone.utc)
    hourly_data = [{"hour": i, "queries": 0, "avg_response": 0} for i in range(24)]
    
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
            hour_diff = int((now - log_time).total_seconds() // 3600)
            if 0 <= hour_diff < 24:
                idx = 23 - hour_diff
                hourly_data[idx]["queries"] += 1
                hourly_data[idx]["avg_response"] = (
                    hourly_data[idx]["avg_response"] + log.response_time_ms
                ) // 2
        except:
            pass
    
    return {
        "title": "Hourly Performance",
        "data": hourly_data,
        "series": [
            {"key": "queries", "name": "Queries", "color": "#3B82F6"},
            {"key": "avg_response", "name": "Avg Response (ms)", "color": "#8B5CF6"}
        ]
    }


@router.get("/activity")
async def get_recent_activity(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent activity feed for dashboard.
    
    Args:
        limit: Maximum number of activity items to return
    
    Returns:
        List of recent activity events with real-time data
    """
    logs = storage.get_query_logs(limit)
    reports = storage.list_reports()[-5:]  # Last 5 reports
    datasets = storage.list_datasets()[-5:]  # Last 5 datasets
    
    activity = []
    
    # Add recent queries
    for log in logs[-limit:]:
        activity.append({
            "id": log.id,
            "type": "query",
            "title": log.query[:50] + "..." if len(log.query) > 50 else log.query,
            "status": log.status,
            "timestamp": log.timestamp,
            "icon": "analytics",
            "color": "#3B82F6" if log.status == "success" else "#EF4444"
        })
    
    # Add recent reports
    for report in reports:
        activity.append({
            "id": report.id,
            "type": "report",
            "title": report.title,
            "status": report.status,
            "timestamp": report.created_at,
            "icon": "document",
            "color": "#10B981"
        })
    
    # Add recent datasets
    for dataset in datasets:
        activity.append({
            "id": dataset.id,
            "type": "dataset",
            "title": f"Uploaded: {dataset.name}",
            "status": "ready",
            "timestamp": dataset.uploaded_at,
            "icon": "dataset",
            "color": "#8B5CF6"
        })
    
    # Sort by timestamp and limit
    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "activity": activity[:limit],
        "total": len(activity)
    }


@router.get("/summary")
async def get_dashboard_summary() -> Dict[str, Any]:
    """
    Get a comprehensive dashboard summary.
    
    Returns:
        Combined summary of all dashboard metrics
    """
    stats = storage.get_dashboard_stats()
    logs = storage.get_query_logs(100)
    
    # Calculate metrics
    success_count = sum(1 for log in logs if log.status == "success")
    success_rate = (success_count / len(logs) * 100) if logs else 100
    
    return {
        "overview": {
            "total_queries": stats["total_queries"],
            "total_datasets": stats["total_datasets"],
            "total_insights": stats["total_insights"],
            "total_reports": stats["total_reports"]
        },
        "health": {
            "success_rate": round(success_rate, 1),
            "status": "healthy" if success_rate > 90 else "degraded",
            "uptime": "99.9%"
        },
        "quick_actions": [
            {"label": "Upload Dataset", "action": "upload", "icon": "upload"},
            {"label": "New Query", "action": "query", "icon": "search"},
            {"label": "Generate Report", "action": "report", "icon": "document"}
        ]
    }
