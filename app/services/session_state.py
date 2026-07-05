def initialize_state():

    return {
        "filters": {},
        "group_by": None,
        "sort_by": None,
        "aggregation": None
    }


def update_session_state(
    previous_state,
    filters,
    group_by=None,
    sort_by=None,
    aggregation=None
):

    updated_state = {
        "filters": {},
        "group_by": None,
        "sort_by": None,
        "aggregation": None
    }

    # =========================================
    # PRESERVE EXISTING NON-FILTER STATE
    # =========================================
    if previous_state:

        updated_state.update(previous_state)

    # =========================================
    # IMPORTANT FIX:
    # USE RESOLVED FILTERS DIRECTLY
    # =========================================
    updated_state["filters"] = filters.copy()

    # =========================================
    # UPDATE ANALYTICS STATE
    # =========================================
    if group_by is not None:

        updated_state["group_by"] = group_by

    if sort_by is not None:

        updated_state["sort_by"] = sort_by

    if aggregation is not None:

        updated_state["aggregation"] = aggregation

    return updated_state