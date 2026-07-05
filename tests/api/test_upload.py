from io import BytesIO
from unittest.mock import patch

import pandas as pd


def create_excel():

    dataframe = pd.DataFrame(
        {
            "Priority": ["P1"],
            "Status": ["Resolved"],
        }
    )

    stream = BytesIO()

    dataframe.to_excel(
        stream,
        index=False,
    )

    stream.seek(0)

    return stream


@patch("app.routes.api.ticket_engine.load_dataset")
def test_upload_success(
    mock_load,
    client,
):

    mock_load.return_value = {
        "success": True,
    }

    response = client.post(
        "/upload",
        files={
            "file": (
                "tickets.xlsx",
                create_excel(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200

    assert response.json()["success"] is True


def test_upload_invalid_extension(
    client,
):

    response = client.post(
        "/upload",
        files={
            "file": (
                "tickets.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
