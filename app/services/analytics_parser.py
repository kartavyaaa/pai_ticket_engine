def detect_analytics_intent(query):

    q = query.lower()

    result = {
        "group_by": None,
        "sort_by": None,
        "aggregation": None
    }

    # =====================================
    # GROUPING
    # =====================================
    if "group by" in q:

        if "assigned" in q:
            result["group_by"] = "assigned_group"

        elif "priority" in q:
            result["group_by"] = "priority"

        elif "status" in q:
            result["group_by"] = "status"

    # =====================================
    # SORTING
    # =====================================
    if "sort by" in q:

        if "priority" in q:
            result["sort_by"] = "priority"

        elif "date" in q:
            result["sort_by"] = "date"

    # =====================================
    # AGGREGATION
    # =====================================
    if "count" in q:

        result["aggregation"] = "count"

    return result