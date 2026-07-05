"""
ticket_engine.py

Production Ticket Engine for the PAI Ticket Engine.

Responsibilities
----------------
- Owns the current dataset.
- Coordinates AI parsing.
- Resolves conversational filter conflicts.
- Delegates filtering to FilterEngine.
- Delegates response generation to ResponseFormatter.

This module intentionally contains NO business logic.
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from app.core.logging import logger
from app.core.exceptions import TicketEngineError

from app.services.dataset_store import dataset_store
from app.services.filter_engine import filter_engine
from app.services.response_formatter import ResponseFormatter
from app.services.schema_profiler import profile_schema
from app.services.conflict_resolver import (
    resolve_filter_conflicts,
)
from app.services.ai_parser import parse_query_with_ai


class TicketEngine:
    """
    Main orchestration layer for the PAI Ticket Engine.

    This class coordinates the complete execution pipeline while
    delegating all business logic to dedicated services.
    """

    def __init__(self) -> None:

        self.dataset_store = dataset_store

        logger.info("TicketEngine initialized.")

    # =====================================================
    # DATASET LOADING
    # =====================================================

    def load_dataset(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Loads a ticket dataset into the DatasetStore.
        """

        if dataframe is None or dataframe.empty:
            raise TicketEngineError(
                "Cannot load an empty dataset."
            )

        schema_map = profile_schema(dataframe)

        self.dataset_store.set_dataset(
            dataframe=dataframe,
            schema_map=schema_map,
        )

        logger.info(
            "Dataset loaded successfully (%s rows).",
            len(dataframe),
        )

        return ResponseFormatter.message(
            "Dataset loaded successfully.",
            meta={
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
            },
        )

    # =====================================================
    # DATASET STATUS
    # =====================================================

    def has_dataset(self) -> bool:
        """
        Returns True if a dataset has been loaded.
        """

        return (
            self.dataset_store.dataframe
            is not None
        )

    # =====================================================
    # QUERY EXECUTION
    # =====================================================

    def execute_query(
        self,
        query: str,
        previous_filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Executes a natural-language query against
        the currently loaded ticket dataset.
        """

        start_time = time.perf_counter()

        if not self.has_dataset():

            return {
                "response": ResponseFormatter.error(
                    "No ticket dataset loaded."
                ),
                "filters": {},
                "metadata": {},
            }

        dataframe = self.dataset_store.dataframe
        schema_map = self.dataset_store.schema_map

        logger.info(
            "Executing query: %s",
            query,
        )

        try:

            filters = parse_query_with_ai(
                query,
            )

            if not filters:

                return {
                    "response": ResponseFormatter.error(
                        "Unable to understand the query."
                    ),
                    "filters": {},
                    "metadata": {},
                }

            logger.info(
                "AI extracted filters: %s",
                filters,
            )

            # ============================================
            # CONVERSATION-AWARE FILTER MERGING
            # ============================================

            if previous_filters:

                filters = resolve_filter_conflicts(
                    previous_filters=previous_filters,
                    current_filters=filters,
                )

                logger.info(
                    "Merged filters: %s",
                    filters,
                )

            # ============================================
            # FILTER DATASET
            # ============================================

            filtered_df = filter_engine.apply_filters(
                dataframe=dataframe,
                schema_map=schema_map,
                filters=filters,
            )

            execution_time = round(
                (
                    time.perf_counter() - start_time
                )
                * 1000,
                2,
            )

            # ============================================
            # COUNT QUERY
            # ============================================

            if filters.get("count"):

                response = ResponseFormatter.count(
                    count=len(filtered_df),
                    meta={
                        "execution_time_ms": execution_time,
                    },
                )

            # ============================================
            # NO RESULTS
            # ============================================

            elif filtered_df.empty:

                response = ResponseFormatter.message(
                    "No matching tickets found.",
                    meta={
                        "execution_time_ms": execution_time,
                    },
                )

            # ============================================
            # DATAFRAME RESULT
            # ============================================

            else:

                response = ResponseFormatter.dataframe(
                    filtered_df,
                    meta={
                        "execution_time_ms": execution_time,
                    },
                )

            logger.info(
                "Query completed in %.2f ms.",
                execution_time,
            )

            return {
                "response": response,
                "filters": filters,
                "metadata": {
                    "query": query,
                    "execution_time_ms": execution_time,
                    "rows_scanned": len(dataframe),
                    "rows_returned": len(filtered_df),
                    "filters_applied": list(filters.keys()),
                },
            }

        except TicketEngineError as exc:

            logger.exception(
                "TicketEngine error."
            )

            return {
                "response": ResponseFormatter.error(
                    str(exc),
                ),
                "filters": {},
                "metadata": {},
            }

        except Exception:

            logger.exception(
                "Unexpected TicketEngine error."
            )

            return {
                "response": ResponseFormatter.error(
                    "An unexpected error occurred while processing the query."
                ),
                "filters": {},
                "metadata": {},
            }


ticket_engine = TicketEngine()