"""
AI Analyst API Routes (Production)

Backward-compatible AI analysis endpoints integrating with the core agent.
"""

from typing import Dict, Any, Optional
import logging
import os
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.query import Query as QueryModel
from app.models.dataset import Dataset
from app.models.activity import Activity
from app.api.deps import OptionalUser

# Import legacy agent core
# We treat this as a service, though it's in root for now
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from agent_core import DataAnalystAgent, AgentConfig
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("agent_core.py not found. AI features will be limited.")

# Define models directly here to avoid ImportErrors above
class QuestionRequest(BaseModel):
    question: str
    context: Dict[str, Any] = {}
    session_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    question: str
    code_generated: str
    result: Any
    explanation: str
    status: str
    usage: Optional[Any] = None
    session_id: Optional[str] = None
    query_id: Optional[str] = None

router = APIRouter(prefix="/analyze", tags=["AI Analyst"])
logger = logging.getLogger(__name__)

# Initialize agent
if AGENT_AVAILABLE:
    config = AgentConfig(max_tokens=3000, enable_code_validation=True, max_retries=3)
    agent = DataAnalystAgent(config)
else:
    agent = None

@router.post("", response_model=AnalysisResponse)
async def analyze_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(OptionalUser),
):
    """
    Analyze a data question using the AI agent.
    """
    logger.info(f"Received analysis request: {request.question}")
    
    # Track usage if authenticated
    query_log = None
    if current_user:
        query_log = QueryModel(
            user_id=current_user.id,
            query_text=request.question,
            status="processing",
            source="ai_agent",
            session_id=request.session_id
        )
        db.add(query_log)
        db.commit()
        
        # Inject API keys from DB into environment for agent_core
        try:
            from app.models.settings_model import ApiKey
            from app.core.security import decrypt_api_key
            user_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
            for k in user_keys:
                os.environ[k.key_name] = decrypt_api_key(k.key_value_encrypted)
        except Exception as e:
            logger.warning(f"Could not load user API keys: {e}")
    
    try:
        # Check if agent is available
        if not AGENT_AVAILABLE or not agent:
            # Return offline fallback
            from server import _offline_analyze_router
            result = _offline_analyze_router(request.question)
            
            response = AnalysisResponse(
                question=request.question,
                code_generated="# Offline fallback",
                result=result,
                explanation=result.get("summary", "Offline analysis performed."),
                status="success"
            )
        else:
            # Prepare context
            if request.context and "dataset_id" in request.context:
                dataset_id = request.context["dataset_id"]
                dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if dataset and os.path.exists(dataset.file_path):
                    pass
            
            # Multi-turn Context Resolution
            augmented_question = request.question
            if request.session_id:
                past_queries = db.query(QueryModel).filter(
                    QueryModel.session_id == request.session_id,
                    QueryModel.status == "completed"
                ).order_by(QueryModel.created_at.desc()).limit(3).all()
                
                if past_queries:
                    history = "Previous conversation sequence:\n"
                    # Reverse because we queried desc()
                    for pq in reversed(past_queries):
                        history += f"User: {pq.query_text}\n"
                        resp_text = "System provided a chart or data table response."
                        if pq.response:
                            try:
                                resp_data = json.loads(pq.response)
                                summary = resp_data.get('summary', '') or resp_data.get('explanation', '')
                                if summary:
                                    resp_text = summary
                            except:
                                pass
                        history += f"System: {resp_text}\n\n"
                    
                    augmented_question = history + f"Current Task/Question: {request.question}"
            
            # 5-minute Caching Check
            from datetime import timedelta
            five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
            
            cached_query = db.query(QueryModel).filter(
                QueryModel.user_id == current_user.id,
                QueryModel.query_text == augmented_question,
                QueryModel.status == "completed",
                QueryModel.created_at >= five_mins_ago
            ).order_by(QueryModel.created_at.desc()).first()
            
            if cached_query and cached_query.response:
                logger.info(f"Cache hit! Reusing AI output from {cached_query.id}")
                cached_data = json.loads(cached_query.response)
                response = AnalysisResponse(
                    question=request.question,
                    code_generated="# Served from cache",
                    result=cached_data,
                    explanation=cached_data.get("summary", "Cached response."),
                    status="success",
                    usage={"provider": "cache", "total_tokens": 0},
                    session_id=request.session_id,
                    query_id=str(query_log.id) if query_log else None
                )
            else:
                # Use the agent
                result = await agent.process_question(
                    question=augmented_question, 
                    context=request.context
                )
                
                # Map standard agent payload to AnalysisResponse
                response = AnalysisResponse(
                    question=request.question, # maintain original question reference
                    code_generated=result.get("code", ""),
                    result=result.get("output", {}),
                    explanation=result.get("explanation", ""),
                    status="success" if result.get("execution_success") else "error",
                    usage=result.get("usage", None),
                    session_id=request.session_id,
                    query_id=str(query_log.id) if query_log else None
                )
            
        # Update log
        if query_log:
            query_log.status = "completed"
            query_log.response = json.dumps(response.result) if hasattr(response, 'result') else str(response)
            db.commit()
            
            # Log activity
            activity = Activity(
                user_id=current_user.id,
                activity_type="analyze",
                title=f"AI Analysis: {request.question[:50]}...",
                status="success",
            )
            db.add(activity)
            db.commit()
            
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if query_log:
            query_log.status = "failed"
            query_log.response = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))
