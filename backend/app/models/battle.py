import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Float

from app.config.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Battle(Base):
    __tablename__ = "battles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    prompt = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    status = Column(String(20), default="completed")
    responses = Column(JSON, nullable=True)
    winner = Column(String(100), nullable=True)
    total_votes = Column(Integer, default=0)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
