from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database.database import Base

from sqlalchemy import JSON

class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, index=True)

    user_message = Column(Text)

    ai_response = Column(Text)

    intent_data = Column(JSON, nullable=True)

    session_state = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )