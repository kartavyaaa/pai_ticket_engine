from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import Conversation


async def create_conversation(
    db: AsyncSession,
    session_id: str,
    user_message: str,
    ai_response: str,
    intent_data: dict = None,
    session_state: dict = None
):

    conversation = Conversation(
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        intent_data=intent_data,
        session_state=session_state
    )

    db.add(conversation)

    await db.commit()
    await db.refresh(conversation)

    return conversation


async def get_conversations(
    db: AsyncSession,
    session_id: str
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
    )

    return result.scalars().all()

async def get_recent_conversations(
    db: AsyncSession,
    session_id: str,
    limit: int = 5
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )

    conversations = result.scalars().all()

    return list(reversed(conversations))