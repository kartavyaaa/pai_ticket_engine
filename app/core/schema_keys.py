"""
Canonical schema keys used throughout the PAI Ticket Engine.

The schema profiler maps user dataset columns to these logical keys.
All downstream services should reference these constants instead of
hardcoded strings.
"""

from __future__ import annotations


class SchemaKeys:
    """
    Logical field names produced by the Schema Profiler.

    Example:

        {
            "priority": "Priority",
            "status": "Current Status",
            "description": "Ticket Summary"
        }

    Other modules should always use SchemaKeys.PRIORITY
    instead of "priority".
    """

    PRIORITY = "priority"

    STATUS = "status"

    ASSIGNED_GROUP = "assigned_group"

    DESCRIPTION = "description"

    CREATED_DATE = "created_date"

    CATEGORY = "category"

    SUBCATEGORY = "subcategory"

    TICKET_ID = "ticket_id"

    CUSTOMER = "customer"

    REGION = "region"

    LOCATION = "location"

    SEVERITY = "severity"

    RESOLUTION = "resolution"

    OWNER = "owner"

    ASSIGNEE = "assignee"

    CREATED_BY = "created_by"

    CLOSED_DATE = "closed_date"

    UPDATED_DATE = "updated_date"