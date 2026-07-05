from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class QueryRequest(BaseModel):
    """
    User query payload.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language query."
    )

    session_id: str | None = Field(
        default=None,
        description="Conversation session."
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty.")

        return value


class QueryResult(BaseModel):
    """
    Standardized query response.
    """

    session_id: str

    result: dict[str, Any]

    session_state: dict[str, Any]


class UploadInfo(BaseModel):
    """
    Information returned after dataset upload.
    """

    message: str

    rows: int

    columns: list[str]


class ErrorResponse(BaseModel):
    """
    Generic error model.
    """

    detail: str


class HealthResponse(BaseModel):

    message: str


class DatasetMetadata(BaseModel):

    filename: str | None

    rows: int

    columns: int

    uploaded_at: str | None


class HistoryResponse(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    history: list[Any]