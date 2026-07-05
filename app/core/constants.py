"""
Application-wide constants used across the PAI Ticket Engine.
"""

from __future__ import annotations


class FilterKeys:
    PRIORITY = "priority"
    STATUS = "status"
    ASSIGNED_GROUP = "assigned_group"
    DESCRIPTION = "description"
    DATE_FROM = "date_from"
    DATE_TO = "date_to"
    COUNT = "count"


SUPPORTED_FILTERS = {
    FilterKeys.PRIORITY,
    FilterKeys.STATUS,
    FilterKeys.ASSIGNED_GROUP,
    FilterKeys.DESCRIPTION,
    FilterKeys.DATE_FROM,
    FilterKeys.DATE_TO,
    FilterKeys.COUNT,
}


class ResponseTypes:
    MESSAGE = "message"
    DATAFRAME = "dataframe"
    COUNT = "count"
    ERROR = "error"
    ANALYTICS = "analytics"


class SemanticMap:
    TERMS = {
        "connection": [
            "connection",
            "failed",
            "unable",
            "timeout",
            "unreachable",
            "disconnect",
            "lost",
        ],
        "login": [
            "login",
            "authentication",
            "unauthorized",
            "credential",
            "access",
        ],
        "traffic": [
            "traffic",
            "imbalance",
            "drop",
            "less traffic",
            "no traffic",
        ],
        "outage": [
            "outage",
            "down",
            "unavailable",
            "failure",
        ],
        "sla": [
            "sla",
            "breach",
            "violation",
        ],
    }

class MetadataKeys:
    EXECUTION_TIME_MS = "execution_time_ms"
    FILTERS_APPLIED = "filters_applied"
    DATASET_ROWS = "dataset_rows"
    MODEL = "model"
    SESSION_ID = "session_id"