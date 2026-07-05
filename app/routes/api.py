"""
api.py

Primary FastAPI routes for the PAI Ticket Engine.
"""

from __future__ import annotations

import io
import uuid

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger

from app.database.database import get_db
from app.database.crud import (
    create_conversation,
    get_conversations,
    get_recent_conversations,
)

from app.routes.schemas import QueryRequest

from app.services.ticket_engine import ticket_engine
from app.services.memory_formatter import summarize_response
from app.services.query_rewriter import rewrite_query
from app.services.analytics_parser import detect_analytics_intent
from app.services.session_state import (
    initialize_state,
    update_session_state,
)

router = APIRouter()


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/")
async def home():

    return {
        "success": True,
        "message": "PAI API is running 🚀",
    }


# =========================================================
# DATASET UPLOAD
# =========================================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
):

    logger.info(
        "Dataset upload requested: %s",
        file.filename,
    )

    try:

        contents = await file.read()

        if file.filename.lower().endswith(
            (
                ".xlsx",
                ".xls",
            )
        ):

            dataframe = pd.read_excel(
                io.BytesIO(contents)
            )

        elif file.filename.lower().endswith(
            ".csv"
        ):

            dataframe = pd.read_csv(
                io.BytesIO(contents)
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="Unsupported file format.",
            )

        dataframe.columns = [
            column.strip()
            for column in dataframe.columns
        ]

        upload_result = ticket_engine.load_dataset(
            dataframe
        )

        logger.info(
            "Dataset uploaded successfully."
        )

        return {
            "success": True,
            "result": upload_result,
        }

    except HTTPException:

        raise

    except Exception:

        logger.exception(
            "Dataset upload failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process uploaded dataset.",
        )


# =========================================================
# QUERY ENDPOINT
# =========================================================

@router.post("/query")
async def query_engine(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a natural language query against the
    currently loaded dataset.
    """

    query = (
        payload.query or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="No query provided.",
        )

    session_id = (
        payload.session_id
        or str(uuid.uuid4())
    )

    logger.info(
        "Query received for session %s",
        session_id,
    )

    previous_filters = {}

    previous_state = initialize_state()

    history = await get_recent_conversations(
        db=db,
        session_id=session_id,
    )

    if history:

        latest = history[-1]

        if latest.intent_data:
            previous_filters = latest.intent_data

        if latest.session_state:
            previous_state = latest.session_state

    rewritten_query = rewrite_query(
        current_query=query,
        previous_filters=previous_filters,
    )

    logger.info(
        "Rewritten query: %s",
        rewritten_query,
    )

    analytics_intent = detect_analytics_intent(
        rewritten_query
    )

    engine_result = ticket_engine.execute_query(
        query=rewritten_query,
        previous_filters=previous_filters,
    )

    response = engine_result.get(
        "response"
    )

    filters = engine_result.get(
        "filters",
        {},
    )

    metadata = engine_result.get(
        "metadata",
        {},
    )

    updated_state = update_session_state(
        previous_state=previous_state,
        filters=filters,
        group_by=analytics_intent.get(
            "group_by"
        ),
        sort_by=analytics_intent.get(
            "sort_by"
        ),
        aggregation=analytics_intent.get(
            "aggregation"
        ),
    )

    ai_summary = summarize_response(
        response
    )

    await create_conversation(
        db=db,
        session_id=session_id,
        user_message=query,
        ai_response=ai_summary,
        intent_data=filters,
        session_state=updated_state,
    )

    logger.info(
        "Conversation stored successfully."
    )

    logger.info(
        "Returning response to session %s.",
        session_id,
    )

    return {
        "success": True,
        "session_id": session_id,
        "result": response,
        "metadata": metadata,
        "session_state": updated_state,
    }


# =========================================================
# CHAT HISTORY
# =========================================================

@router.get("/history/{session_id}")
async def chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns stored conversation history.
    """

    history = await get_conversations(
        db=db,
        session_id=session_id,
    )

    return {
        "success": True,
        "history": history,
    }