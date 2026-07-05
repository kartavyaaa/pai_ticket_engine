"""
filter_engine.py

Responsible for applying all ticket filters to a dataset.

This service is intentionally stateless and should not
interact with APIs, OpenAI, databases or DatasetStore.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import re

from app.core.schema_keys import SchemaKeys
from app.core.constants import FilterKeys, SemanticMap
from app.core.logging import logger


@dataclass(slots=True)
class FilterContext:
    """
    Carries the state of a single filtering operation
    throughout the filtering pipeline.
    """
    dataframe: pd.DataFrame

    schema_map: dict[str, str]

    filters: dict[str, Any]

    relevance_scores: pd.Series

    active_filters: list[str]


class FilterEngine:
    """
    Applies all ticket filters.

    Pipeline

        Hard Filters
            ↓
        Semantic Search
            ↓
        Ranking
            ↓
        Sorted DataFrame
    """

    def apply_filters(
        self,
        dataframe: pd.DataFrame,
        schema_map: dict[str, str],
        filters: dict[str, Any],
    ) -> pd.DataFrame:

        logger.info("Starting filter pipeline.")

        context = FilterContext(
            dataframe=dataframe.copy(),
            schema_map=schema_map,
            filters=filters,
            relevance_scores=pd.Series(
                0,
                index=dataframe.index,
                dtype=int,
            ),
            active_filters=[],
        )

        hard_filter_pipeline = (
            self._apply_priority,
            self._apply_status,
            self._apply_assignment_group,
            self._apply_date_range,
        )

        for step in hard_filter_pipeline:

            step(context)

            if context.dataframe.empty:

                logger.info(
                    "Filter pipeline terminated early. No rows remaining."
                )

                return context.dataframe.reset_index(drop=True)

        self._apply_description(context)

        return self._finalize(context)

    def _apply_priority(
        self,
        context: FilterContext,
    ) -> None:

        self._apply_exact_match_filter(
            context=context,
            filter_key=FilterKeys.PRIORITY,
            schema_key=SchemaKeys.PRIORITY,
            log_name="Priority",
        )


    def _apply_exact_match_filter(
        self,
        context: FilterContext,
        filter_key: str,
        schema_key: str,
        log_name: str,
    ) -> None:
        """
        Applies an exact-match filter such as
        Priority, Status or Assignment Group.
        """

        if filter_key not in context.filters:

            logger.debug(
                "%s filter not requested.",
                log_name,
            )

            return

        column = self._get_schema_column(
            context,
            schema_key,
        )

        if not column:
            logger.warning("%s column not found.", log_name)
            return

        value = str(
            context.filters[filter_key]
        ).lower()

        normalized = self._normalize_series(
            context.dataframe[column]
        )

        context.dataframe = context.dataframe.loc[
            normalized == value
        ].copy()

        context.active_filters.append(filter_key)

        logger.info(
            "%s filter applied. Remaining rows: %s",
            log_name,
            len(context.dataframe),
        )

    def _apply_status(
        self,
        context: FilterContext,
    ) -> None:
        self._apply_exact_match_filter(
            context=context,
            filter_key=FilterKeys.STATUS,
            schema_key=SchemaKeys.STATUS,
            log_name="Status",
        )


    def _apply_assignment_group(
        self,
        context: FilterContext,
    ) -> None:
        self._apply_exact_match_filter(
            context=context,
            filter_key=FilterKeys.ASSIGNED_GROUP,
            schema_key=SchemaKeys.ASSIGNED_GROUP,
            log_name="Assignment Group",
        )

    def _apply_date_range(
        self,
        context: FilterContext,
    ) -> None:
        """
        Applies date range filtering using
        date_from and date_to.
        """

        if (
            FilterKeys.DATE_FROM not in context.filters
            and FilterKeys.DATE_TO not in context.filters
        ):
            return

        column = self._get_schema_column(
            context,
            SchemaKeys.CREATED_DATE,
        )

        if not column:
            logger.warning("Created Date column not found.")
            return

        try:

            dates = pd.to_datetime(
                context.dataframe[column],
                errors="coerce",
            )

            mask = pd.Series(
                True,
                index=context.dataframe.index,
            )

            if FilterKeys.DATE_FROM in context.filters:

                start = pd.to_datetime(
                    context.filters[FilterKeys.DATE_FROM],
                    errors="coerce",
                )

                if pd.notna(start):

                    mask &= dates >= start
                    context.active_filters.append(
                        FilterKeys.DATE_FROM
                    )

            if FilterKeys.DATE_TO in context.filters:

                end = pd.to_datetime(
                    context.filters[FilterKeys.DATE_TO],
                    errors="coerce",
                )

                if pd.notna(end):

                    mask &= dates <= end
                    context.active_filters.append(
                        FilterKeys.DATE_TO
                    )

            context.dataframe = context.dataframe.loc[mask].copy()

            logger.info(
                "Date filter applied. Remaining rows: %s",
                len(context.dataframe),
            )

        except Exception:

            logger.exception(
                "Failed to apply date filter."
            )

    def _apply_description(
        self,
        context: FilterContext,
    ) -> None:
        """
        Applies semantic description matching
        and calculates relevance scores.
        """

        if FilterKeys.DESCRIPTION not in context.filters:
            return

        column = self._get_schema_column(
            context,
            SchemaKeys.DESCRIPTION,
        )

        if not column:

            logger.warning(
                "Description column not found."
            )

            return

        search_text = str(
            context.filters[
                FilterKeys.DESCRIPTION
            ]
        )

        expanded_terms = self._expand_terms(
            search_text
        )

        normalized = self._normalize_series(
            context.dataframe[column]
        )

        scores = pd.Series(
            0,
            index=context.dataframe.index,
            dtype=int,
        )

        search_lower = search_text.lower()

        for term in expanded_terms:

            matches = normalized.str.contains(
                term,
                na=False,
                regex=False,
            )

            weight = (
                3
                if term in search_lower
                else 1
            )

            scores += matches.astype(int) * weight

        context.relevance_scores = scores

        context.active_filters.append(
            FilterKeys.DESCRIPTION
        )

        logger.info(
            "Semantic description search applied."
        )

    def _get_schema_column(
        self,
        context: FilterContext,
        schema_key: str,
    ) -> str | None:
        """
        Returns the actual dataframe column mapped
        to the logical schema key.
        """

        return context.schema_map.get(schema_key)
    
    def _normalize_series(
        self,
        series: pd.Series,
    ) -> pd.Series:
        """
        Normalizes a pandas Series for
        case-insensitive searching.
        """

        return (
            series.fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )
    
    def _expand_terms(
        self,
        text: str,
    ) -> list[str]:
        """
        Expands semantic keywords using the
        configured semantic dictionary.
        """

        text = text.lower()

        tokens = re.findall(
            r"\w+",
            text.lower(),
        )

        expanded = set(tokens)

        for keyword, synonyms in SemanticMap.TERMS.items():

            if keyword in text:

                expanded.update(synonyms)

        return sorted(expanded)

    def _finalize(
        self,
        context: FilterContext,
    ) -> pd.DataFrame:
        """
        Finalizes the filtering pipeline.

        Applies semantic relevance ranking
        only if a description search was used.
        """

        dataframe = context.dataframe

        if FilterKeys.DESCRIPTION in context.active_filters:

            dataframe = dataframe.loc[
                context.relevance_scores > 0
            ]

            dataframe = dataframe.assign(
                __pai_relevance=context.relevance_scores.loc[
                    dataframe.index
                ]
            )

            dataframe = dataframe.sort_values(
                "__pai_relevance",
                ascending=False,
            )

            dataframe = dataframe.drop(
                columns="__pai_relevance"
            )

        logger.info(
            "Filtering completed. %s rows returned.",
            len(dataframe),
        )

        return dataframe.reset_index(drop=True)
    
# Singleton instance used throughout the application
filter_engine = FilterEngine()