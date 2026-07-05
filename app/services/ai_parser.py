"""
ai_parser.py

OpenAI-powered natural language parser for the
PAI Ticket Engine.
"""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

SUPPORTED_FILTERS = {
    "priority",
    "status",
    "assigned_group",
    "description",
    "date_from",
    "date_to",
    "count",
}


SYSTEM_PROMPT = """
You are the AI parser for the PAI Ticket Engine.

Your ONLY task is to convert a user's natural language
query into a valid JSON object.

Rules:

- Return ONLY JSON.
- Never explain.
- Never use markdown.
- Never wrap the response.
- Never invent filter names.

Allowed filter keys:

priority
status
assigned_group
description
date_from
date_to
count

Examples

User:
Show critical tickets

Output:
{
    "priority":"critical"
}

User:
Network tickets

Output:
{
    "assigned_group":"network"
}

User:
How many resolved tickets this month?

Output:
{
    "status":"resolved",
    "count":true
}
"""


def _sanitize_filters(
    filters: dict[str, Any],
) -> dict[str, Any]:
    """
    Removes unsupported or empty filters.
    """

    cleaned = {}

    for key, value in filters.items():

        if key not in SUPPORTED_FILTERS:
            continue

        if value in (
            None,
            "",
            [],
            {},
        ):
            continue

        cleaned[key] = value

    return cleaned

def parse_query_with_ai(
    query: str,
) -> dict[str, Any]:
    """
    Parses a natural-language ticket query into
    structured filters using OpenAI.
    """

    logger.info(
        "Parsing query with AI: %s",
        query,
    )

    try:

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            temperature=0,
        )

        content = response.output_text.strip()

        logger.debug(
            "Raw AI response: %s",
            content,
        )

        filters = json.loads(content)

        if not isinstance(filters, dict):

            logger.warning(
                "AI returned a non-object JSON response."
            )

            return {}

        filters = _sanitize_filters(filters)

        logger.info(
            "Parsed filters: %s",
            filters,
        )

        return filters

    except json.JSONDecodeError:

        logger.exception(
            "Failed to decode AI JSON response."
        )

        return {}

    except Exception:

        logger.exception(
            "OpenAI parser failed."
        )

        return {}