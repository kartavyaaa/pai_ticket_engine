def rewrite_query(
    current_query: str,
    previous_filters: dict
):

    if not previous_filters:
        return current_query

    rewritten_parts = []

    # =========================================
    # STATUS
    # =========================================
    if previous_filters.get("status"):

        rewritten_parts.append(
            f"{previous_filters['status']} tickets"
        )

    # =========================================
    # PRIORITY
    # =========================================
    if previous_filters.get("priority"):

        rewritten_parts.append(
            f"{previous_filters['priority']} priority"
        )

    # =========================================
    # ASSIGNED GROUP
    # =========================================
    if previous_filters.get("assigned_group"):

        rewritten_parts.append(
            f"assigned to {previous_filters['assigned_group']}"
        )

    memory_context = " ".join(rewritten_parts)

    rewritten_query = f"""
{current_query}

Context:
{memory_context}
"""

    return rewritten_query.strip()