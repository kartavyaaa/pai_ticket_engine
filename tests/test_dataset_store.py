from app.services.dataset_store import DatasetState


def test_initial_state():

    store = DatasetState()

    assert store.loaded is False
    assert store.dataframe is None
    assert store.row_count == 0
    assert store.column_count == 0


def test_set_dataset(
    ticket_dataframe,
    schema_map,
):

    store = DatasetState()

    store.set_dataset(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
    )

    assert store.loaded is True
    assert store.dataframe is not None
    assert store.schema_map == schema_map
    assert store.row_count == len(ticket_dataframe)
    assert store.column_count == len(ticket_dataframe.columns)


def test_clear_dataset(
    ticket_dataframe,
    schema_map,
):

    store = DatasetState()

    store.set_dataset(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
    )

    store.clear()

    assert store.loaded is False
    assert store.dataframe is None
    assert store.schema_map == {}
    assert store.column_map == {}
    assert store.row_count == 0
    assert store.column_count == 0


def test_filename_optional(
    ticket_dataframe,
    schema_map,
):

    store = DatasetState()

    store.set_dataset(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
    )

    assert store.filename is None


def test_uploaded_timestamp(
    ticket_dataframe,
    schema_map,
):

    store = DatasetState()

    store.set_dataset(
        dataframe=ticket_dataframe,
        schema_map=schema_map,
    )

    assert store.uploaded_at is not None