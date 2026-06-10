from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.services.ai_orchestrator import AIOrchestrator


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = AIOrchestrator()

    async def create_session(
        self,
        user_id: str,
        title: str,
        model: str = "gemini-2.5-flash"
    ):
        session = ChatSession(
            user_id=user_id,
            title=title,
            model=model
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    async def get_sessions(self, user_id: str):
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    async def get_session(
        self,
        session_id: str,
        user_id: str
    ):
        return (
            self.db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            .first()
        )

    async def get_messages(self, session_id: str):
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    async def send_message(
        self,
        session_id: str,
        message: str
    ):
        session = (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id)
            .first()
        )

        if not session:
            raise ValueError("Session not found")

        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=message
        )

        self.db.add(user_message)
        self.db.commit()

        result = await self.orchestrator.call_gemini(
            message
        )

        if result["status"] != "success":
            raise ValueError(
                result.get(
                    "error",
                    "Failed to generate response"
                )
            )

        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=result["response"]
        )

        self.db.add(assistant_message)
        self.db.commit()

        return result["response"]

    async def delete_session(
        self,
        session_id: str,
        user_id: str
    ):
        session = (
            self.db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            .first()
        )

        if not session:
            return False

        (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == session_id
            )
            .delete()
        )

        self.db.delete(session)
        self.db.commit()

        return True
