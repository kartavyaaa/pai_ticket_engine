def summarize_response(result):

    if not result:
        return "No response"

    response_type = result.get("type")

    # =====================================
    # MESSAGE RESPONSE
    # =====================================
    if response_type == "message":

        return result.get("data", "Message returned")

    # =====================================
    # DATAFRAME RESPONSE
    # =====================================
    if response_type == "dataframe":

        data = result.get("data", [])

        row_count = len(data)

        return f"Returned {row_count} ticket records"

    # =====================================
    # FALLBACK
    # =====================================
    return str(result)