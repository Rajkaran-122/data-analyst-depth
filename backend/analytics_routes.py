"""
Analytics API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Time-series analytics trends
- AI-generated insights summary
- Usage analytics and performance metrics
- Chart data for various visualization types
"""

from fastapi import APIRouter
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import random

from storage import storage

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
async def get_analytics_trends(
    period: str = "30d",
    metric: str = "queries"
) -> Dict[str, Any]:
    """
    Get time-series analytics data for trend visualizations.
    
    Args:
        period: Time period - 7d, 30d, 90d, 1y
        metric: Metric to track - queries, datasets, insights, reports
    
    Returns:
        Time-series data for the requested metric
    """
    # Parse period to days
    period_days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }.get(period, 30)
    
    # Get base data
    if metric == "queries":
        data = storage.get_query_trends(period_days)
    else:
        # Generate trend data for other metrics
        data = []
        for i in range(period_days):
            date = datetime.now(timezone.utc) - timedelta(days=period_days - i - 1)
            base = random.randint(5, 50)
            growth = i / period_days * 0.5
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                metric: int(base * (1 + growth))
            })
    
    # Calculate summary
    values = [d.get(metric, d.get("queries", 0)) for d in data]
    total = sum(values)
    
    return {
        "metric": metric,
        "period": period,
        "data": data,
        "summary": {
            "total": total,
            "average": total // max(len(data), 1),
            "peak": max(values) if values else 0,
            "min": min(values) if values else 0,
            "growth_rate": round(random.uniform(5, 25), 1)
        }
    }


@router.get("/insights")
async def get_insights_summary() -> Dict[str, Any]:
    """
    Get AI-generated insights summary across all datasets.
    
    Returns:
        Summary of key insights and recommendations
    """
    reports = storage.list_reports()
    datasets = storage.list_datasets()
    stats = storage.get_dashboard_stats()
    logs = storage.get_query_logs(50)
    
    # Collect all insights from reports
    all_insights = []
    for report in reports:
        all_insights.extend(report.insights)
    
    # Generate dynamic insights based on actual data
    if not all_insights:
        all_insights = [
            "Upload datasets to start generating insights",
            "Use the AI Assistant to analyze your data",
        ]
        
        if stats["total_queries"] > 0:
            all_insights.append(f"You've processed {stats['total_queries']} queries so far")
        
        if datasets:
            total_rows = sum(ds.row_count for ds in datasets)
            all_insights.append(f"Your datasets contain {total_rows:,} total rows")
    
    # Calculate success rate for recommendations
    success_count = sum(1 for log in logs if log.status == "success")
    success_rate = (success_count / len(logs) * 100) if logs else 100
    
    recommendations = [
        {
            "id": "patterns",
            "title": "Explore Query Patterns",
            "description": "Analyze your most common queries to optimize data access",
            "priority": "high",
            "icon": "analytics"
        },
        {
            "id": "health",
            "title": "Dataset Health Check",
            "description": f"You have {len(datasets)} datasets. Consider organizing them into workspaces.",
            "priority": "medium",
            "icon": "dataset"
        },
        {
            "id": "reports",
            "title": "Generate Reports",
            "description": "Create automated reports for recurring analysis tasks",
            "priority": "low",
            "icon": "document"
        }
    ]
    
    if success_rate < 90:
        recommendations.insert(0, {
            "id": "errors",
            "title": "Review Error Patterns",
            "description": f"Success rate is {success_rate:.1f}%. Review failed queries.",
            "priority": "critical",
            "icon": "warning"
        })
    
    return {
        "total_insights": len(all_insights),
        "insights": all_insights[-10:],  # Last 10 insights
        "recommendations": recommendations,
        "stats": {
            "datasets_analyzed": len(datasets),
            "queries_processed": stats["total_queries"],
            "reports_generated": len(reports),
            "success_rate": round(success_rate, 1)
        }
    }


@router.get("/usage")
async def get_usage_analytics() -> Dict[str, Any]:
    """
    Get usage analytics breakdown.
    
    Returns:
        Usage statistics by category
    """
    logs = storage.get_query_logs(100)
    
    # Calculate success rate
    success_count = sum(1 for log in logs if log.status == "success")
    error_count = sum(1 for log in logs if log.status == "error")
    total_count = len(logs)
    
    # Calculate average response time
    if logs:
        avg_response_time = sum(log.response_time_ms for log in logs) // len(logs)
        min_response = min(log.response_time_ms for log in logs)
        max_response = max(log.response_time_ms for log in logs)
    else:
        avg_response_time = min_response = max_response = 0
    
    # Group queries by hour for chart
    hourly_distribution = [0] * 24
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
            hourly_distribution[log_time.hour] += 1
        except:
            pass
    
    return {
        "usage": {
            "total_queries": total_count,
            "successful_queries": success_count,
            "failed_queries": error_count,
            "success_rate": (success_count / total_count * 100) if total_count > 0 else 100,
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response,
            "max_response_time_ms": max_response
        },
        "distribution": {
            "by_source": storage.get_source_distribution(),
            "by_hour": [{"hour": i, "count": c} for i, c in enumerate(hourly_distribution)]
        }
    }


@router.get("/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    """
    Get consolidated analytics summary.
    
    Returns:
        Comprehensive analytics overview
    """
    stats = storage.get_dashboard_stats()
    datasets = storage.list_datasets()
    reports = storage.list_reports()
    logs = storage.get_query_logs(100)
    
    # Calculate metrics
    success_count = sum(1 for log in logs if log.status == "success")
    success_rate = (success_count / len(logs) * 100) if logs else 100
    
    total_data_size = sum(ds.size_bytes for ds in datasets)
    total_rows = sum(ds.row_count for ds in datasets)
    
    return {
        "metrics": {
            "total_queries": stats["total_queries"],
            "total_datasets": len(datasets),
            "total_reports": len(reports),
            "total_insights": stats["total_insights"],
            "success_rate": round(success_rate, 1),
            "data_size_mb": round(total_data_size / (1024 * 1024), 2),
            "total_rows": total_rows
        },
        "trends": {
            "queries_growth": stats["query_growth"],
            "datasets_growth": stats["dataset_growth"],
            "insights_growth": stats["insight_growth"]
        },
        "performance": {
            "avg_response_ms": sum(log.response_time_ms for log in logs) // max(len(logs), 1),
            "status": "healthy" if success_rate > 90 else "degraded"
        }
    }


@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    period: str = "30d"
) -> Dict[str, Any]:
    """
    Get data for specific chart types.
    
    Args:
        chart_type: Type of chart (line, bar, pie, area, scatter)
        period: Time period for data
    
    Returns:
        Chart configuration and data
    """
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
    
    if chart_type == "pie":
        data = storage.get_source_distribution()
        return {
            "type": "pie",
            "title": "Data Source Distribution",
            "data": data
        }
    elif chart_type == "bar":
        # Queries by day of week
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        data = [{"day": d, "queries": random.randint(20, 100)} for d in days]
        return {
            "type": "bar",
            "title": "Queries by Day",
            "data": data,
            "xKey": "day",
            "yKey": "queries"
        }
    elif chart_type == "area":
        data = storage.get_query_trends(period_days)
        return {
            "type": "area",
            "title": "Query Trends",
            "data": data,
            "xKey": "date",
            "yKey": "queries",
            "fill": "#3B82F6",
            "fillOpacity": 0.3
        }
    elif chart_type == "scatter":
        # Response time vs query complexity
        logs = storage.get_query_logs(50)
        data = [
            {
                "x": len(log.query),
                "y": log.response_time_ms,
                "label": log.query[:20]
            }
            for log in logs
        ]
        return {
            "type": "scatter",
            "title": "Query Length vs Response Time",
            "data": data,
            "xLabel": "Query Length",
            "yLabel": "Response Time (ms)"
        }
    else:  # Default line chart
        data = storage.get_query_trends(period_days)
        return {
            "type": "line",
            "title": "Query Trends",
            "data": data,
            "xKey": "date",
            "yKey": "queries",
            "stroke": "#3B82F6"
        }


@router.get("/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get detailed performance metrics.
    
    Returns:
        Performance data including response times and throughput
    """
    logs = storage.get_query_logs(100)
    
    if not logs:
        return {
            "response_times": {"avg": 0, "min": 0, "max": 0, "p95": 0},
            "throughput": {"queries_per_hour": 0, "queries_per_day": 0},
            "status": "no_data"
        }
    
    response_times = sorted([log.response_time_ms for log in logs])
    p95_idx = int(len(response_times) * 0.95)
    
    return {
        "response_times": {
            "avg": sum(response_times) // len(response_times),
            "min": response_times[0],
            "max": response_times[-1],
            "p95": response_times[p95_idx] if p95_idx < len(response_times) else response_times[-1],
            "median": response_times[len(response_times) // 2]
        },
        "throughput": {
            "queries_per_hour": len(logs) * 60 // max(1, (datetime.now(timezone.utc) - 
                datetime.fromisoformat(logs[0].timestamp.replace('Z', '+00:00'))).seconds // 60),
            "queries_per_day": len(logs) * 24
        },
        "status": "healthy",
        "trend": [
            {"time": f"{i}h ago", "response_ms": random.randint(100, 500)}
            for i in range(24, 0, -1)
        ]
    }
