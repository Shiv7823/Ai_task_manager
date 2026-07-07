from click import prompt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse
from app.services.gemini_service import enrich_task, score_task_priority, summarize_task_list
from pydantic import BaseModel
from typing import Optional
from app.services.gemini_service import gemini_model, _safe_json_parse
router = APIRouter()

class EnrichRequest(BaseModel):
    title: str
    description: Optional[str] = None

class ScoreResponse(BaseModel):
    task_id: int
    score: int
    suggested_priority: str
    reasoning: str
    risk_if_delayed: str

class SummaryResponse(BaseModel):
    total_tasks: int
    briefing: str

@router.post("/enrich/{task_id}", response_model=TaskResponse)
def ai_enrich_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = enrich_task(task.title, task.description)

    if not task.description:
        task.description = result.get("description", task.description)
    task.ai_summary = result.get("summary")
    task.ai_priority_reason = result.get("priority_reason")
    task.ai_enriched = True
    task.priority = result.get("priority", "medium")

    if not task.deadline:
        days = result.get("deadline_days", 7)
        task.deadline = datetime.utcnow() + timedelta(days=int(days))

    db.commit()
    db.refresh(task)
    return task

@router.post("/enrich-new", response_model=dict)
def ai_enrich_new(
    payload: EnrichRequest
):
    result = enrich_task(payload.title, payload.description)
    return result

@router.get("/score/{task_id}", response_model=ScoreResponse)
def ai_score_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    description = task.description or task.title
    result = score_task_priority(task.title, description, task.priority.value)

    return {
        "task_id": task_id,
        "score": result.get("score", 5),
        "suggested_priority": result.get("suggested_priority", task.priority.value),
        "reasoning": result.get("reasoning", ""),
        "risk_if_delayed": result.get("risk_if_delayed", "")
    }

@router.get("/daily-briefing", response_model=SummaryResponse)
def ai_daily_briefing(
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(
        Task.status.in_(["todo", "in_progress"])
    ).order_by(Task.priority.desc()).limit(20).all()

    task_dicts = [
        {"title": t.title, "priority": t.priority.value, "status": t.status.value}
        for t in tasks
    ]

    briefing = summarize_task_list(task_dicts)
    return {"total_tasks": len(tasks), "briefing": briefing}