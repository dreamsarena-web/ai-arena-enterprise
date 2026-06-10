from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSendRequest,
    ChatSendResponse,
)

from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/session",
    response_model=ChatSessionResponse
)
async def create_session(
    request: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)

    return await service.create_session(
        user_id=current_user.id,
        title=request.title,
        model=request.model
    )


@router.get(
    "/sessions",
    response_model=list[ChatSessionResponse]
)
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)

    return await service.get_sessions(
        current_user.id
    )


@router.get(
    "/session/{session_id}"
)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)

    session = await service.get_session(
        session_id,
        current_user.id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = await service.get_messages(
        session_id
    )

    return {
        "session": session,
        "messages": messages
    }


@router.post(
    "/message",
    response_model=ChatSendResponse
)
async def send_message(
    request: ChatSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)

    response = await service.send_message(
        request.session_id,
        request.message
    )

    return {
        "response": response
    }


@router.delete(
    "/session/{session_id}"
)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)

    deleted = await service.delete_session(
        session_id,
        current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "success": True
    }
