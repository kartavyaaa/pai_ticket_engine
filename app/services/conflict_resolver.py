def resolve_filter_conflicts(
    previous_filters,
    current_filters
):

    if not previous_filters:
        previous_filters = {}

    if not current_filters:
        current_filters = {}

    # =====================================================
    # STEP 1
    # CLEAN CURRENT FILTERS FIRST
    # =====================================================
    cleaned_current = current_filters.copy()

    # ---------------------------------------------
    # PRIORITY DOMINATES AMBIGUOUS VALUES
    # ---------------------------------------------
    if (
        "priority" in cleaned_current
        and "assigned_group" in cleaned_current
    ):

        priority_val = str(
            cleaned_current["priority"]
        ).lower()

        group_val = str(
            cleaned_current["assigned_group"]
        ).lower()

        # same semantic token
        if priority_val == group_val:

            print(
                "[CONFLICT RESOLVER] "
                "Removing ambiguous assigned_group "
                "from CURRENT filters"
            )

            del cleaned_current["assigned_group"]

    # =====================================================
    # STEP 2
    # APPLY MEMORY CONFLICT RESOLUTION
    # =====================================================
    resolved = previous_filters.copy()

    for current_key, current_value in cleaned_current.items():

        for old_key, old_value in list(resolved.items()):

            # ---------------------------------------------
            # SAME VALUE, DIFFERENT DIMENSION
            # ---------------------------------------------
            if (
                current_key != old_key
                and str(current_value).lower()
                == str(old_value).lower()
            ):

                print(
                    "[CONFLICT RESOLVER] "
                    f"Removing conflicting memory filter: "
                    f"{old_key}={old_value}"
                )

                del resolved[old_key]

    # =====================================================
    # STEP 3
    # APPLY CLEAN FILTERS
    # =====================================================
    resolved.update(cleaned_current)

    return resolved