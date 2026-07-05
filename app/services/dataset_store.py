from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
import pandas as pd


@dataclass
class DatasetState:
    """
    Holds the currently loaded dataset and
    all metadata derived from it.
    """

    dataframe: pd.DataFrame | None = None

    column_map: dict = field(default_factory=dict)

    schema_map: dict = field(default_factory=dict)

    uploaded_at: datetime | None = None

    filename: str | None = None

    row_count: int = 0

    column_count: int = 0

    @property
    def loaded(self) -> bool:
        return self.dataframe is not None

    def clear(self):

        self.dataframe = None

        self.column_map = {}

        self.schema_map = {}

        self.filename = None

        self.uploaded_at = None

        self.row_count = 0

        self.column_count = 0

    def set_dataset(
        self,
        dataframe: pd.DataFrame,
        schema_map: dict,
        column_map: dict | None = None,
        filename: str | None = None,
    ) -> None:
        """
        Stores the currently loaded dataset along with any
        available metadata.

        column_map and filename are optional because the
        TicketEngine should only care about the dataset and
        its logical schema.
        """

        self.dataframe = dataframe

        self.schema_map = schema_map

        self.column_map = column_map or {}

        self.filename = filename

        self.uploaded_at = datetime.now(UTC)
        
        self.row_count = len(dataframe)

        self.column_count = len(dataframe.columns)


dataset_store = DatasetState()