"""
response_formatter.py

Centralized response formatting for the PAI Ticket Engine.

Every backend response should be generated from this class.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


class ResponseFormatter:
    """
    Responsible for creating standardized responses returned
    by the Ticket Engine.

    Supported response types:
    - message
    - dataframe
    - error
    - count
    """

    @staticmethod
    def message(text: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "type": "message",
            "success": True,
            "data": text,
            "meta": meta or {}
        }

    @staticmethod
    def error(text: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "type": "error",
            "success": False,
            "data": text,
            "meta": meta or {}
        }

    @staticmethod
    def count(count: int, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "type": "count",
            "success": True,
            "count": count,
            "data": f"Found {count} matching tickets.",
            "meta": meta or {}
        }

    @staticmethod
    def dataframe(
        dataframe: pd.DataFrame,
        limit: int = 100,
        meta: dict[str, Any] | None = None
    ) -> dict[str, Any]:

        total_rows = len(dataframe)
        dataframe = dataframe.head(limit)

        return {
            "type": "dataframe",
            "success": True,
            "rows": len(dataframe),
            "total_rows": total_rows,
            "data": dataframe.to_dict(
                orient="records"
            ),
            "meta": meta or {}
        }

    @staticmethod
    def analytics(
        title: str,
        data: dict[str, Any],
        meta: dict[str, Any] | None = None
    ) -> dict[str, Any]:

        return {
            "type": "analytics",
            "success": True,
            "title": title,
            "data": data,
            "meta": meta or {}
        }