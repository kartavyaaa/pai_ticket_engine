def build_context_prompt(
    current_query: str,
    history: list
):

    if not history:
        return current_query

    context_lines = []

    for convo in history:

        context_lines.append(
            f"User: {convo.user_message}"
        )

        context_lines.append(
            f"PAI: {convo.ai_response}"
        )

    context_block = "\n".join(context_lines)

    enhanced_query = f"""
Previous Conversation Context:
{context_block}

Current User Query:
{current_query}
"""

    return enhanced_query.strip()