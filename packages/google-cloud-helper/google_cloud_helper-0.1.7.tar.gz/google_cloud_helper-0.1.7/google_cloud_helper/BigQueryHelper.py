import logging
from datetime import datetime
from typing import Dict, List

import pandas as pd
from google.cloud import bigquery, exceptions
from google.cloud.bigquery.schema import SchemaField

logger = logging.getLogger(__name__)


class BigQueryHelper:

    def __init__(self, project_id: str) -> None:
        """Initializes the BigQueryHelper.

        Args:
            project_id: The Google Cloud project ID.
        """
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)

    def exists_table(self, table_id: str) -> bool:
        """Checks if a BigQuery table exists.

        Args:
            table_id: The ID of the table in the format 'project.dataset.table'.

        Returns:
            True if the table exists, False otherwise.
        """
        try:
            self.client.get_table(table_id)
            return True
        except exceptions.NotFound:
            return False

    def create_table_labels(
        self, cost_category: str, triggered_by: str, caller: str
    ) -> Dict[str, str]:
        """Returns a dictionary of default labels for BigQuery tables.

        Args:
            cost_category: The cost category of the table.
            triggered_by: The name of the service that triggered the table creation.
            caller: either 'service' or 'user'

        Returns:
            A dictionary of default labels for BigQuery tables.
        """
        return {
            "cost-category": cost_category,
            "triggered_by": triggered_by,
            "caller": caller,
        }

    def read_table_as_df(self, table_id: str) -> pd.DataFrame:
        """Reads a BigQuery table as a pandas DataFrame.

        Args:
            table_id: The ID of the table to read.

        Returns:
            A pandas DataFrame containing the data from the table.
        """
        return pd.read_gbq(table_id, project_id=self.project_id)

    def create_dataset(self, dataset_id: str, location: str = "europe-west3") -> None:
        """Creates a BigQuery dataset if it doesn't already exist.

        The dataset will be created in the 'europe-west3' location.

        Args:
            dataset_id: The ID of the dataset to create. This should not include
                the project ID.
            location: The location of the dataset. Defaults to 'europe-west3'.
        """
        dataset_ref = f"{self.project_id}.{dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_ref} already exists.")
        except exceptions.NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            self.client.create_dataset(dataset)
            logger.info(f"Created dataset {dataset_ref}.")

    def create_table_from_df(
        self,
        table_id: str,
        df: pd.DataFrame,
        partitioning: str | None = None,
        clustering: List[str] | None = None,
        labels: Dict[str, str] | None = None,
        specific_types: Dict = {},
    ):
        """Creates and populates a BigQuery table from a pandas DataFrame.

        This method infers the schema from the DataFrame. If the table already
        exists, it will be updated. The data from the DataFrame will be loaded
        into the table.

        Args:
            table_id: The ID of the table to create, in the format
                'project.dataset.table'.
            df: The pandas DataFrame to load into the table.
            partitioning: Optional. The name of the column to use for
                time-based partitioning (DAY).
            clustering: Optional. A list of column names to use for clustering.
            labels: Optional. A dictionary of labels to add to the table for
                cost monitoring or organization.
            specific_types: Optional. A dictionary of column names and their BigQuery data types.
        """
        schema = self.generate_bigquery_schema_from_df(
            df, specific_types=specific_types
        )
        table = bigquery.Table(table_id, schema=schema)

        if partitioning:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partitioning,
            )

        if clustering:
            table.clustering_fields = clustering

        if labels:
            table.labels = labels

        self.client.create_table(table, exists_ok=True)
        job = self.client.load_table_from_dataframe(df, table_id)
        job.result()

    def delete_table(self, table_id: str):
        """Deletes a BigQuery table.

        Args:
            table_id: The ID of the table to delete.
        """
        self.client.delete_table(table_id, not_found_ok=True)
        logging.info(f"Deleted table {table_id}")

    def delete_dataset(self, dataset_id: str):
        """Deletes a BigQuery dataset.
        Args:
            dataset_id: The ID of the dataset to delete.
        """
        self.client.delete_dataset(dataset_id, not_found_ok=True)
        logging.info(f"Deleted dataset {dataset_id}")

    def upload_df_to_table(self, table_id: str, df: pd.DataFrame):
        """Uploads a pandas DataFrame to an existing BigQuery table.

        This method appends the data from the DataFrame to the specified table.
        The table must already exist and its schema should be compatible with
        the DataFrame.

        Args:
            table_id: The ID of the target table in the format
                'project.dataset.table'.
            df: The pandas DataFrame to upload.
        """
        logger.info(f"Writing DataFrame to BigQuery table: {table_id} ...")
        try:
            job = self.client.load_table_from_dataframe(df, table_id)
            job.result()
            logger.info(f"DataFrame written to BigQuery table: {table_id}")
        except Exception as e:
            logger.error(f"Error writing DataFrame to BigQuery: {e}")

    def incremental_insert_with_deduplication(
        self,
        table_id: str,
        df: pd.DataFrame,
        id_cols: List[str],
    ):
        """Incrementally inserts data from a DataFrame into a table, avoiding duplicates.

        This method performs a MERGE operation to insert rows from the DataFrame
        that do not already exist in the target table. Duplicates are identified
        based on the `id_cols` columns.

        It works by:
        1. Uploading the DataFrame to a temporary staging table.
        2. Executing a MERGE SQL statement that inserts rows from the staging
           table into the target table if they don't match on the id cols.
        3. Deleting the temporary staging table.

        Args:
            table_id: The ID of the target table for the merge operation, in the
                format 'project.dataset.table'.
            df: The pandas DataFrame containing new data to insert.
            id_cols: A list of column names that constitute the id cols
                for deduplication.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_table_id = f"temp_staging_{timestamp}"
        temp_table_ref = f"{self.project_id}.{table_id.split('.')[1]}.{temp_table_id}"

        logger.info(f"Target table: {table_id}")
        logger.info(f"temp table: {temp_table_id}")

        target_schema = self.client.get_table(table_id).schema

        # Upload to staging
        job_config = bigquery.LoadJobConfig(
            schema=target_schema, write_disposition="WRITE_TRUNCATE"
        )
        self.client.load_table_from_dataframe(
            df, temp_table_ref, job_config=job_config
        ).result()

        # Build merge SQL
        match_condition = " AND ".join([f"T.{col} = S.{col}" for col in id_cols])
        columns = [field.name for field in target_schema]
        insert_columns = ", ".join(columns)
        insert_values = ", ".join([f"S.{col}" for col in columns])

        merge_sql = f"""
        MERGE `{table_id}` T
        USING `{temp_table_ref}` S
        ON {match_condition}
        WHEN NOT MATCHED THEN
          INSERT ({insert_columns}) VALUES ({insert_values})
        """

        self.client.query(merge_sql).result()
        self.client.delete_table(temp_table_ref, not_found_ok=True)

    def generate_bigquery_schema_from_df(
        self, df: pd.DataFrame, specific_types: Dict = {}
    ) -> List[SchemaField]:
        """Generates a BigQuery schema from a pandas DataFrame.

        This function infers BigQuery data types from the DataFrame's dtypes.
        It supports nested structures (RECORD) and repeated fields (arrays/lists).

        - Python lists are mapped to REPEATED mode.
        - Python dicts are mapped to RECORD type.

        Args:
            df: The pandas DataFrame from which to infer the schema.

        Returns:
            A list of `google.cloud.bigquery.schema.SchemaField` objects
            representing the BigQuery schema.
        """
        TYPE_MAPPING = {
            "i": "INTEGER",
            "u": "NUMERIC",
            "b": "BOOLEAN",
            "f": "FLOAT",
            "O": "STRING",
            "S": "STRING",
            "U": "STRING",
            "M": "TIMESTAMP",
        }
        TYPE_MAPPING.update(specific_types)
        schema = []
        for column, dtype in df.dtypes.items():
            val = df[column].iloc[0]
            mode = "REPEATED" if isinstance(val, list) else "NULLABLE"

            if isinstance(val, dict) or (
                mode == "REPEATED" and isinstance(val[0], dict)
            ):
                fields = self.generate_bigquery_schema_from_df(
                    pd.json_normalize(val), specific_types
                )
            else:
                fields = []

            type = "RECORD" if fields else TYPE_MAPPING.get(dtype.kind)
            schema.append(
                SchemaField(
                    name=column,
                    field_type=type,
                    mode=mode,
                    fields=fields,
                )
            )
        return schema

    def sql2df(self, query: str) -> pd.DataFrame:
        """
        Executes a BigQuery SQL query and returns the result as a pandas DataFrame.
        Args:
            query: The SQL query to execute.

        Returns:
            A pandas DataFrame containing the query results.
        """
        try:
            df = self.client.query(query).to_dataframe()
            return df
        except Exception as e:
            logger.error(f"Error reading DataFrame from BigQuery: {e}")
            return None

    def update_table(self, table_id: str, df: pd.DataFrame, id_cols: List[str]) -> None:
        """
        Atomically updates rows from df into a BigQuery table
        based on matching id_cols using MERGE.

        Args:
            table_id (str): Full BQ table ID (e.g. 'project.dataset.table')
            df (pd.DataFrame): DataFrame with new data
            id_cols (list[str]): List of columns that uniquely identify rows
        """
        if not isinstance(id_cols, list):
            raise ValueError("id_cols must be a list of column names")

        # Deduplicate df
        df = df.drop_duplicates(subset=id_cols, keep="first")

        # Step 1: Upload df to a temporary table
        temp_table_id = table_id + "_temp_merge"
        job = self.client.load_table_from_dataframe(
            df,
            temp_table_id,
            job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
        )
        job.result()
        logger.info(f"Loaded {len(df)} rows into temporary table {temp_table_id}")

        # Step 2: Build MERGE statement
        id_match = " AND ".join(
            [f"T.{col} IS NOT DISTINCT FROM S.{col}" for col in id_cols]
        )
        update_set = ", ".join(
            [f"{col} = S.{col}" for col in df.columns if col not in id_cols]
        )
        insert_cols = ", ".join(df.columns)
        insert_vals = ", ".join([f"S.{col}" for col in df.columns])

        merge_sql = f"""
        MERGE `{table_id}` T
        USING (
            SELECT DISTINCT {', '.join(df.columns)} FROM `{temp_table_id}`
        ) S
        ON {id_match}
        WHEN MATCHED THEN
          UPDATE SET {update_set}
        WHEN NOT MATCHED THEN
          INSERT ({insert_cols}) VALUES ({insert_vals})
        """

        # Step 3: Execute MERGE
        self.client.query(merge_sql).result()
        logger.info(f"MERGE completed: updated and inserted rows into {table_id}")

        # Step 4: Drop temp table
        self.client.delete_table(temp_table_id, not_found_ok=True)
        logger.info(f"Dropped temporary table {temp_table_id}")
