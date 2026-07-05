"""
exceptions.py

Centralized exception definitions and handlers
for the PAI Ticket Engine.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import logger


# =====================================================
# APPLICATION EXCEPTIONS
# =====================================================

class PAIException(Exception):
    """
    Base exception for all PAI-specific errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TicketEngineError(PAIException):
    """
    Raised when the Ticket Engine encounters
    a recoverable processing error.
    """


class DatasetError(PAIException):
    """
    Raised for dataset loading or validation errors.
    """


class AIParserError(PAIException):
    """
    Raised when the AI parser fails.
    """


# =====================================================
# FASTAPI HANDLER
# =====================================================

async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error.",
        },
    )