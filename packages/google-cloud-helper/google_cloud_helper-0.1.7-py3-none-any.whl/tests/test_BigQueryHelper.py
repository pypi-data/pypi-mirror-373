import logging
from unittest.mock import ANY, MagicMock, patch

import pandas as pd
import pytest
from google.cloud import bigquery, exceptions
from google.cloud.bigquery.schema import SchemaField

from google_cloud_helper.BigQueryHelper import BigQueryHelper


@pytest.fixture
def mock_bigquery_client():
    """Fixture to mock the BigQuery client."""
    with patch(
        "google_cloud_helper.BigQueryHelper.bigquery.Client", autospec=True
    ) as mock_client_constructor:
        mock_client = mock_client_constructor.return_value
        yield mock_client


@pytest.fixture
def bq_helper(mock_bigquery_client):
    """Fixture to provide a BigQueryHelper instance with a mocked client."""
    return BigQueryHelper(project_id="test-project")


def test_init():
    """Tests the constructor of BigQueryHelper."""
    with patch(
        "google_cloud_helper.BigQueryHelper.bigquery.Client"
    ) as mock_client_constructor:
        helper = BigQueryHelper(project_id="test-project")
        mock_client_constructor.assert_called_once_with(project="test-project")
        assert helper.project_id == "test-project"
        assert helper.client == mock_client_constructor.return_value


def test_exists_table_true(bq_helper, mock_bigquery_client):
    """Tests exists_table when the table exists."""
    table_id = "test-project.ds.table"
    bq_helper.exists_table(table_id)
    mock_bigquery_client.get_table.assert_called_once_with(table_id)


def test_exists_table_false(bq_helper, mock_bigquery_client):
    """Tests exists_table when the table does not exist."""
    table_id = "test-project.ds.table"
    mock_bigquery_client.get_table.side_effect = exceptions.NotFound("Table not found")
    assert not bq_helper.exists_table(table_id)
    mock_bigquery_client.get_table.assert_called_once_with(table_id)


def test_create_dataset_already_exists(bq_helper, mock_bigquery_client, caplog):
    """Tests create_dataset when the dataset already exists."""
    dataset_id = "my_dataset"
    dataset_ref = f"test-project.{dataset_id}"
    with caplog.at_level(logging.INFO):
        bq_helper.create_dataset(dataset_id)
        assert f"Dataset {dataset_ref} already exists." in caplog.text
    mock_bigquery_client.get_dataset.assert_called_once_with(dataset_ref)
    mock_bigquery_client.create_dataset.assert_not_called()


def test_create_dataset_new(bq_helper, mock_bigquery_client, caplog):
    """Tests create_dataset when the dataset does not exist."""
    dataset_id = "my_dataset"
    dataset_ref = f"test-project.{dataset_id}"
    mock_bigquery_client.get_dataset.side_effect = exceptions.NotFound("Not found")

    with caplog.at_level(logging.INFO):
        bq_helper.create_dataset(dataset_id)
        assert f"Created dataset {dataset_ref}." in caplog.text

    mock_bigquery_client.get_dataset.assert_called_once_with(dataset_ref)
    mock_bigquery_client.create_dataset.assert_called_once()
    created_dataset_arg = mock_bigquery_client.create_dataset.call_args[0][0]
    assert isinstance(created_dataset_arg, bigquery.Dataset)
    assert (
        created_dataset_arg.reference.path
        == f"/projects/test-project/datasets/{dataset_id}"
    )
    assert created_dataset_arg.location == "europe-west3"


@patch(
    "google_cloud_helper.BigQueryHelper.BigQueryHelper.generate_bigquery_schema_from_df"
)
def test_create_table_from_df(mock_schema_gen, bq_helper, mock_bigquery_client):
    """Tests create_table_from_df with all options."""
    df = pd.DataFrame({"ts": [pd.Timestamp("2023-01-01")], "id": [1], "cat": ["A"]})
    mock_schema = [SchemaField("ts", "TIMESTAMP"), SchemaField("id", "INTEGER")]
    mock_schema_gen.return_value = mock_schema

    table_id = "test-project.ds.tbl"
    partitioning = "ts"
    clustering = ["id"]
    labels = {"env": "test"}

    mock_job = MagicMock()
    mock_bigquery_client.load_table_from_dataframe.return_value = mock_job

    bq_helper.create_table_from_df(
        table_id, df, partitioning=partitioning, clustering=clustering, labels=labels
    )

    mock_schema_gen.assert_called_once_with(df)

    # Check table creation call
    mock_bigquery_client.create_table.assert_called_once_with(ANY, exists_ok=True)
    created_table_arg = mock_bigquery_client.create_table.call_args[0][0]
    assert isinstance(created_table_arg, bigquery.Table)
    assert created_table_arg.schema == mock_schema
    assert created_table_arg.labels == labels
    assert created_table_arg.clustering_fields == clustering
    assert (
        created_table_arg.time_partitioning.type_ == bigquery.TimePartitioningType.DAY
    )
    assert created_table_arg.time_partitioning.field == partitioning

    # Check data load call
    mock_bigquery_client.load_table_from_dataframe.assert_called_once_with(df, table_id)
    mock_job.result.assert_called_once()


def test_upload_df_to_table_success(bq_helper, mock_bigquery_client, caplog):
    """Tests successful upload of a DataFrame."""
    df = pd.DataFrame({"col1": [1, 2]})
    table_id = "test-project.ds.tbl"
    mock_job = MagicMock()
    mock_bigquery_client.load_table_from_dataframe.return_value = mock_job

    with caplog.at_level(logging.INFO):
        bq_helper.upload_df_to_table(table_id, df)
        assert f"Writing DataFrame to BigQuery table: {table_id} ..." in caplog.text
        assert f"DataFrame written to BigQuery table: {table_id}" in caplog.text

    mock_bigquery_client.load_table_from_dataframe.assert_called_once_with(df, table_id)
    mock_job.result.assert_called_once()


def test_upload_df_to_table_failure(bq_helper, mock_bigquery_client, caplog):
    """Tests failed upload of a DataFrame."""
    df = pd.DataFrame({"col1": [1, 2]})
    table_id = "test-project.ds.tbl"
    error_message = "Something went wrong"
    mock_bigquery_client.load_table_from_dataframe.side_effect = Exception(
        error_message
    )

    with caplog.at_level(logging.ERROR):
        bq_helper.upload_df_to_table(table_id, df)
        assert f"Error writing DataFrame to BigQuery: {error_message}" in caplog.text


@patch("google_cloud_helper.BigQueryHelper.datetime")
def test_incremental_insert_with_deduplication(
    mock_dt, bq_helper, mock_bigquery_client
):
    """Tests the incremental insert (MERGE) operation."""
    mock_dt.now.return_value.strftime.return_value = "20230101120000"

    table_id = "test-project.my_dataset.my_table"
    df = pd.DataFrame({"id": [3, 4], "value": ["c", "d"]})
    unique_key = ["id"]

    # Mock get_table for schema retrieval
    mock_schema = [SchemaField("id", "INTEGER"), SchemaField("value", "STRING")]
    mock_table = MagicMock()
    mock_table.schema = mock_schema
    mock_bigquery_client.get_table.return_value = mock_table

    # Mock job results
    mock_load_job = MagicMock()
    mock_query_job = MagicMock()
    mock_bigquery_client.load_table_from_dataframe.return_value = mock_load_job
    mock_bigquery_client.query.return_value = mock_query_job

    bq_helper.incremental_insert_with_deduplication(table_id, df, unique_key)

    # 1. Check get_table call for schema
    mock_bigquery_client.get_table.assert_called_once_with(table_id)

    # 2. Check staging table upload
    temp_table_ref = "test-project.my_dataset.temp_staging_20230101120000"
    mock_bigquery_client.load_table_from_dataframe.assert_called_once()
    call_args, call_kwargs = mock_bigquery_client.load_table_from_dataframe.call_args
    assert call_args[0].equals(df)
    assert call_args[1] == temp_table_ref
    job_config = call_kwargs["job_config"]
    assert job_config.schema == mock_schema
    assert job_config.write_disposition == "WRITE_TRUNCATE"
    mock_load_job.result.assert_called_once()

    # 3. Check MERGE query
    expected_merge_sql = f"""
        MERGE `{table_id}` T
        USING `{temp_table_ref}` S
        ON T.id = S.id
        WHEN NOT MATCHED THEN
          INSERT (id, value) VALUES (S.id, S.value)
    """
    mock_bigquery_client.query.assert_called_once()
    actual_sql = mock_bigquery_client.query.call_args[0][0]
    assert " ".join(actual_sql.split()) == " ".join(expected_merge_sql.split())
    mock_query_job.result.assert_called_once()

    # 4. Check temp table deletion
    mock_bigquery_client.delete_table.assert_called_once_with(
        temp_table_ref, not_found_ok=True
    )


class TestGenerateSchema:
    """Tests for generate_bigquery_schema_from_df."""

    def _assert_schema_equal(self, s1, s2):
        """Helper to compare lists of SchemaField objects."""
        assert len(s1) == len(s2)
        for f1, f2 in zip(s1, s2):
            assert f1.name == f2.name
            assert f1.field_type == f2.field_type
            assert f1.mode == f2.mode
            self._assert_schema_equal(f1.fields, f2.fields)

    def test_generate_schema_simple_types(self, bq_helper):
        df = pd.DataFrame(
            {
                "my_int": pd.Series([1], dtype="int64"),
                "my_float": pd.Series([1.1], dtype="float64"),
                "my_bool": pd.Series([True], dtype="bool"),
                "my_string": pd.Series(["a"], dtype="object"),
                "my_timestamp": pd.Series([pd.Timestamp("2023-01-01")]),
            }
        )
        schema = bq_helper.generate_bigquery_schema_from_df(df)
        expected_schema = [
            SchemaField("my_int", "INTEGER", "NULLABLE"),
            SchemaField("my_float", "FLOAT", "NULLABLE"),
            SchemaField("my_bool", "BOOLEAN", "NULLABLE"),
            SchemaField("my_string", "STRING", "NULLABLE"),
            SchemaField("my_timestamp", "TIMESTAMP", "NULLABLE"),
        ]
        self._assert_schema_equal(schema, expected_schema)

    def test_generate_schema_repeated_simple_type(self, bq_helper):
        # Note: The current implementation infers repeated simple types as STRING
        # because the DataFrame column's dtype is 'object'.
        df = pd.DataFrame({"my_list": [[1, 2], [3, 4]]})
        schema = bq_helper.generate_bigquery_schema_from_df(df)
        expected_schema = [SchemaField("my_list", "STRING", "REPEATED")]
        self._assert_schema_equal(schema, expected_schema)

    def test_generate_schema_nested_record(self, bq_helper):
        df = pd.DataFrame([{"my_record": {"a": 1, "b": "x"}}])
        schema = bq_helper.generate_bigquery_schema_from_df(df)
        expected_schema = [
            SchemaField(
                "my_record",
                "RECORD",
                "NULLABLE",
                fields=[
                    SchemaField("a", "INTEGER", "NULLABLE"),
                    SchemaField("b", "STRING", "NULLABLE"),
                ],
            )
        ]
        self._assert_schema_equal(schema, expected_schema)

    def test_generate_schema_repeated_record(self, bq_helper):
        df = pd.DataFrame({"my_records": [[{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]]})
        schema = bq_helper.generate_bigquery_schema_from_df(df)
        expected_schema = [
            SchemaField(
                "my_records",
                "RECORD",
                "REPEATED",
                fields=[
                    SchemaField("a", "INTEGER", "NULLABLE"),
                    SchemaField("b", "STRING", "NULLABLE"),
                ],
            )
        ]
        self._assert_schema_equal(schema, expected_schema)

    def test_generate_schema_all_null_column(self, bq_helper):
        """Tests schema for a column with only null values defaults to NULLABLE STRING."""
        df = pd.DataFrame({"my_col": [None, None]})
        schema = bq_helper.generate_bigquery_schema_from_df(df)
        expected_schema = [SchemaField("my_col", "STRING", "NULLABLE")]
        self._assert_schema_equal(schema, expected_schema)
