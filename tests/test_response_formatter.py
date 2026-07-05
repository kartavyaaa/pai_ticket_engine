import pandas as pd

from app.services.response_formatter import ResponseFormatter


def test_message_response():

    result = ResponseFormatter.message("Hello World")

    assert result["type"] == "message"
    assert result["success"] is True
    assert result["data"] == "Hello World"


def test_error_response():

    result = ResponseFormatter.error("Something failed")

    assert result["type"] == "error"
    assert result["success"] is False
    assert result["data"] == "Something failed"


def test_count_response():

    result = ResponseFormatter.count(25)

    assert result["type"] == "count"
    assert result["count"] == 25
    assert result["success"] is True


def test_dataframe_response():

    dataframe = pd.DataFrame(
        {
            "Incident": [1, 2],
            "Priority": ["P1", "P2"],
        }
    )

    result = ResponseFormatter.dataframe(dataframe)

    assert result["type"] == "dataframe"
    assert result["rows"] == 2
    assert result["total_rows"] == 2
    assert len(result["data"]) == 2


def test_dataframe_limit():

    dataframe = pd.DataFrame(
        {
            "A": range(250),
        }
    )

    result = ResponseFormatter.dataframe(
        dataframe,
        limit=100,
    )

    assert result["rows"] == 100
    assert result["total_rows"] == 250


def test_analytics_response():

    result = ResponseFormatter.analytics(
        title="Top Categories",
        data={
            "Authentication": 18,
            "Network": 7,
        },
    )

    assert result["type"] == "analytics"
    assert result["title"] == "Top Categories"
    assert result["success"] is True
