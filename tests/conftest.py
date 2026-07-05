from pathlib import Path

import pandas as pd
import pytest

from app.services.schema_profiler import profile_schema


TEST_DATA = (
    Path(__file__).parent
    / "data"
    / "INC Report.xlsx"
)


@pytest.fixture(scope="session")
def ticket_dataframe():

    df = pd.read_excel(TEST_DATA)

    df.columns = [
        c.strip()
        for c in df.columns
    ]

    return df


@pytest.fixture(scope="session")
def schema_map(ticket_dataframe):

    return profile_schema(ticket_dataframe)