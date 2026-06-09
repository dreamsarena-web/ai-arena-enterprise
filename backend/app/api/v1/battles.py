import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.config.database import get_db
from app.models.battle import Battle
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter()


class BattleRequest(BaseModel):
    prompt: str
    category: Optional[str] = "general"


class BattleResponse(BaseModel):
    id: str
    prompt: str
    category: str
    status: str
    responses: list
    execution_time: float

    class Config:
        from_attributes = True


@router.post("/", response_model=BattleResponse)
async def create_battle(
    request: BattleRequest,
    db: Session = Depends(get_db)
):
    """Create a new AI battle between Gemini and Llama"""

    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Execute battle
    start_time = time.time()
    orchestrator = AIOrchestrator()
    results = await orchestrator.execute_battle(request.prompt)
    execution_time = round(time.time() - start_time, 2)

    # Save to database
    battle = Battle(
        prompt=request.prompt,
        category=request.category,
        status="completed",
        responses=results,
        execution_time=execution_time
    )

    db.add(battle)
    db.commit()
    db.refresh(battle)

    return BattleResponse(
        id=battle.id,
        prompt=battle.prompt,
        category=battle.category,
        status=battle.status,
        responses=results,
        execution_time=execution_time
    )


@router.get("/{battle_id}")
def get_battle(battle_id: str, db: Session = Depends(get_db)):
    """Get battle by ID"""

    battle = db.query(Battle).filter(Battle.id == battle_id).first()

    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")

    return battle


@router.get("/")
def list_battles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all battles"""

    battles = db.query(Battle).order_by(
        Battle.created_at.desc()
    ).offset(skip).limit(limit).all()

    return battles
