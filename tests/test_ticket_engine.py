from unittest.mock import patch

import pandas as pd

from app.services.ticket_engine import TicketEngine
from app.services.response_formatter import ResponseFormatter


def test_no_dataset_loaded():

    engine = TicketEngine()

    engine.dataset_store.clear()

    result = engine.execute_query(
        "Show P1 tickets"
    )

    assert result["response"]["success"] is False
    assert "No ticket dataset" in result["response"]["data"]


def test_load_dataset(
    ticket_dataframe,
):

    engine = TicketEngine()

    response = engine.load_dataset(
        ticket_dataframe
    )

    assert response["success"] is True
    assert engine.has_dataset()


@patch("app.services.ticket_engine.parse_query_with_ai")
def test_execute_priority_query(
    mock_ai,
    ticket_dataframe,
):

    engine = TicketEngine()

    engine.load_dataset(
        ticket_dataframe
    )

    mock_ai.return_value = {
        "priority": "P1",
    }

    result = engine.execute_query(
        "Show P1 tickets"
    )

    assert result["response"]["success"] is True

    assert (
        result["metadata"]["rows_returned"]
        >= 0
    )

    assert (
        result["filters"]["priority"]
        == "P1"
    )


@patch("app.services.ticket_engine.parse_query_with_ai")
def test_count_query(
    mock_ai,
    ticket_dataframe,
):

    engine = TicketEngine()

    engine.load_dataset(
        ticket_dataframe
    )

    mock_ai.return_value = {
        "status": "Resolved",
        "count": True,
    }

    result = engine.execute_query(
        "How many resolved tickets?"
    )

    assert (
        result["response"]["type"]
        == "count"
    )


@patch("app.services.ticket_engine.parse_query_with_ai")
def test_no_results(
    mock_ai,
    ticket_dataframe,
):

    engine = TicketEngine()

    engine.load_dataset(
        ticket_dataframe
    )

    mock_ai.return_value = {
        "priority": "INVALID",
    }

    result = engine.execute_query(
        "Invalid priority"
    )

    assert (
        result["response"]["type"]
        == "message"
    )


@patch("app.services.ticket_engine.parse_query_with_ai")
def test_ai_returns_empty(
    mock_ai,
    ticket_dataframe,
):

    engine = TicketEngine()

    engine.load_dataset(
        ticket_dataframe
    )

    mock_ai.return_value = {}

    result = engine.execute_query(
        "asdasdasd"
    )

    assert (
        result["response"]["success"]
        is False
    )


@patch("app.services.ticket_engine.parse_query_with_ai")
def test_metadata_present(
    mock_ai,
    ticket_dataframe,
):

    engine = TicketEngine()

    engine.load_dataset(
        ticket_dataframe
    )

    mock_ai.return_value = {
        "priority": "P1",
    }

    result = engine.execute_query(
        "Show P1"
    )

    metadata = result["metadata"]

    assert "execution_time_ms" in metadata
    assert "rows_scanned" in metadata
    assert "rows_returned" in metadata
    assert "query" in metadata