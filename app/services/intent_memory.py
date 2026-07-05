def merge_filters(previous_filters, current_filters):

    if not previous_filters:
        previous_filters = {}

    if not current_filters:
        current_filters = {}

    merged = previous_filters.copy()

    merged.update(current_filters)

    return merged