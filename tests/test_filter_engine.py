import pandas as pd

from app.core.schema_keys import SchemaKeys

from app.services.filter_engine import filter_engine
from app.core.constants import FilterKeys


def test_no_filters_returns_everything(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={},
    )

    assert len(result) == len(ticket_dataframe)


def test_priority_filter(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.PRIORITY: "P1",
        },
    )

    expected = ticket_dataframe[
        ticket_dataframe["Priority"]
        .astype(str)
        .str.lower()
        == "p1"
    ]

    assert len(result) == len(expected)


def test_status_filter(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.STATUS: "Resolved",
        },
    )

    expected = ticket_dataframe[
        ticket_dataframe["Status"]
        .astype(str)
        .str.lower()
        == "resolved"
    ]

    assert len(result) == len(expected)


def test_assignment_group_filter(
    ticket_dataframe,
    schema_map,
):

    group = (
        ticket_dataframe[
            "Assigned Group"
        ]
        .dropna()
        .iloc[0]
    )

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.ASSIGNED_GROUP: group,
        },
    )

    expected = ticket_dataframe[
        ticket_dataframe[
            "Assigned Group"
        ]
        .astype(str)
        .str.lower()
        == str(group).lower()
    ]

    assert len(result) == len(expected)


def test_unknown_priority_returns_zero(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.PRIORITY: "INVALID",
        },
    )

    assert result.empty

def test_multiple_filters(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.PRIORITY: "P1",
            FilterKeys.STATUS: "Resolved",
        },
    )

    expected = ticket_dataframe.copy()

    expected = expected[
        expected["Priority"]
        .astype(str)
        .str.lower()
        == "p1"
    ]

    expected = expected[
        expected["Status"]
        .astype(str)
        .str.lower()
        == "resolved"
    ]

    assert len(result) == len(expected)

def test_empty_dataframe(
    ticket_dataframe,
    schema_map,
):

    empty = ticket_dataframe.iloc[0:0].copy()

    result = filter_engine.apply_filters(
        dataframe=empty,
        schema_map=schema_map,
        filters={},
    )

    assert result.empty

def test_missing_priority_column(
    ticket_dataframe,
    schema_map,
):

    broken_schema = schema_map.copy()

    broken_schema.pop(
        SchemaKeys.PRIORITY,
        None,
    )

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=broken_schema,
        filters={
            FilterKeys.PRIORITY: "P1",
        },
    )

    assert len(result) == len(ticket_dataframe)

def test_date_filter(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.DATE_FROM: "2025-01-01",
        },
    )

    assert len(result) <= len(ticket_dataframe)

def test_description_search(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.DESCRIPTION: "traffic",
        },
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

def test_pipeline_early_termination(
    ticket_dataframe,
    schema_map,
):

    result = filter_engine.apply_filters(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
        filters={
            FilterKeys.PRIORITY: "THIS_DOES_NOT_EXIST",
            FilterKeys.STATUS: "Resolved",
        },
    )

    assert result.empty

def test_filter_order_independence(
    ticket_dataframe,
    schema_map,
):

    filters_one = {
        FilterKeys.PRIORITY: "P1",
        FilterKeys.STATUS: "Resolved",
    }

    filters_two = {
        FilterKeys.STATUS: "Resolved",
        FilterKeys.PRIORITY: "P1",
    }

    result_one = filter_engine.apply_filters(
        ticket_dataframe,
        schema_map,
        filters_one,
    )

    result_two = filter_engine.apply_filters(
        ticket_dataframe,
        schema_map,
        filters_two,
    )

    assert len(result_one) == len(result_two)

