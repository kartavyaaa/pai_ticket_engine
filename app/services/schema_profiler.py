import pandas as pd


# =========================================================
# SEMANTIC PATTERNS
# =========================================================
SEMANTIC_PATTERNS = {

    "priority": [
        "priority",
        "severity",
        "impact",
        "urgency"
    ],

    "status": [
        "status",
        "state",
        "incident state",
        "ticket state"
    ],

    "assigned_group": [
        "assigned group",
        "assignment group",
        "queue",
        "team",
        "ops queue"
    ],

    "description": [
        "description",
        "summary",
        "details",
        "remarks",
        "comments"
    ],

    "created_date": [
        "creation date",
        "created",
        "opened",
        "created on"
    ]
}


# =========================================================
# VALUE KEYWORDS
# =========================================================
VALUE_PATTERNS = {

    "priority": [
        "high",
        "medium",
        "low",
        "critical",
        "med"
    ],

    "status": [
        "open",
        "closed",
        "resolved",
        "pending"
    ]
}


# =========================================================
# SCORE COLUMN
# =========================================================
def score_column(
    column_name,
    semantic_role,
    sample_values
):

    score = 0

    col_lower = column_name.lower()

    patterns = SEMANTIC_PATTERNS.get(
        semantic_role,
        []
    )

    # =====================================================
    # EXACT MATCH BOOST
    # =====================================================
    for pattern in patterns:

        # exact column match
        if col_lower == pattern:

            score += 10

        # starts with pattern
        elif col_lower.startswith(pattern):

            score += 7

        # contains pattern
        elif pattern in col_lower:

            score += 4

    # =====================================================
    # VALUE ANALYSIS
    # =====================================================
    value_keywords = VALUE_PATTERNS.get(
        semantic_role,
        []
    )

    lower_values = [
        str(v).lower()
        for v in sample_values
    ]

    for keyword in value_keywords:

        matches = sum(
            keyword in val
            for val in lower_values
        )

        score += matches * 2

    return score


# =========================================================
# PROFILE SCHEMA
# =========================================================
def profile_schema(df: pd.DataFrame):

    schema_map = {}

    columns = list(df.columns)

    # =====================================================
    # SEMANTIC ROLE DETECTION
    # =====================================================
    for semantic_role in SEMANTIC_PATTERNS.keys():

        best_column = None

        best_score = -1

        for column in columns:

            sample_values = (
                df[column]
                .dropna()
                .astype(str)
                .head(30)
                .tolist()
            )

            score = score_column(
                column_name=column,
                semantic_role=semantic_role,
                sample_values=sample_values
            )

            print(
                f"[SCHEMA SCORE] "
                f"{semantic_role} -> {column} = {score}"
            )

            if score > best_score:

                best_score = score

                best_column = column

        # ---------------------------------------------
        # CONFIDENCE THRESHOLD
        # ---------------------------------------------
        if best_score > 0:

            schema_map[semantic_role] = best_column

    return schema_map