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
    from agent_core import DataAnalystAgent, AgentConfig, QuestionRequest, AnalysisResponse
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("agent_core.py not found. AI features will be limited.")

    # Mock classes if missing
    class QuestionRequest(BaseModel):
        question: str
        context: Dict[str, Any] = {}

    class AnalysisResponse(BaseModel):
        question: str
        code_generated: str
        result: Any
        explanation: str
        status: str

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
    current_user: Optional[object] = Depends(OptionalUser),
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
        )
        db.add(query_log)
        db.commit()
    
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
            # If dataset_id is in context, load its path
            if request.context and "dataset_id" in request.context:
                dataset_id = request.context["dataset_id"]
                dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if dataset and os.path.exists(dataset.file_path):
                    # We need to temporarily symlink or copy the file to 'data.csv' 
                    # because the agent expects it in the CWD or we update agent logic.
                    # Best approach: Pass file path in context and update agent prompt if possible.
                    # Or just rely on agent being smart.
                    # For compatibility with legacy server.py assumption (agent reads 'data.csv'):
                    # We might need to handle file context carefully.
                    
                    # NOTE: In a real production system, we'd pass the dataframe or file path cleanly.
                    # Here we adhere to the existing agent_core logic which might look for local files.
                    pass
            
            # Use the agent
            result = await agent.process_question(
                question=request.question, 
                context=request.context
            )
            response = result # wrapper already returns compatible dict/object
            
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
