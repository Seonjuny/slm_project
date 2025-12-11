# app/routers/manage.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.core import memory

router = APIRouter(prefix="/manage", tags=["manage"])


class ResetSessionRequest(BaseModel):
    session_id: str


class ResetResponse(BaseModel):
    status: str


@router.get("/sessions")
def list_sessions():
    return {"sessions": memory.list_sessions()}


@router.post("/reset", response_model=ResetResponse)
def reset_session(req: ResetSessionRequest):
    memory.reset_session(req.session_id)
    return ResetResponse(status=f"session {req.session_id} reset")


@router.post("/reset_all", response_model=ResetResponse)
def reset_all():
    memory.reset_all()
    return ResetResponse(status="all sessions reset")
