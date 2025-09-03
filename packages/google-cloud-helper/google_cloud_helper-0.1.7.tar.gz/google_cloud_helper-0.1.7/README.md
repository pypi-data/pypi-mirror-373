# google-cloud-helper

This repository contains common functions for easy access to Google Cloud Infrastructure, such as Big Query or Google buckets.


## Example Usage

```python
from google_cloud_helper.BigQueryHelper import BigQueryHelper
from google_cloud_helper.GoogleBucketHelper import GoogleBucketHelper
from google_cloud_helper.SecretManagerHelper import SecretManagerHelper

# BigQuery
bq_helper = BigQueryHelper("your-gcp-project-id")
exists = bq_helper.table_exists("your-gcp-project-id.dataset.table")
print(f"Table exists: {exists}")

# Google Cloud Storage
bucket_helper = GoogleBucketHelper("your-gcp-project-id")
bucket_exists = bucket_helper.bucket_exists("your-bucket-name")
print(f"Bucket exists: {bucket_exists}")

# Secret Manager
secret_helper = SecretManagerHelper()
my_secret = secret_helper.get_secret("your-gcp-project-id", "your-secret-id")
print("Successfully retrieved secret!")
```

## Available Functions

### BigQueryHelper

<!-- BIGQUERYHELPER START -->
- `create_dataset(self, dataset_id, location)`
- `create_table_from_df(self, table_id, df, partitioning, clustering, labels, specific_types)`
- `create_table_labels(self, cost_category, triggered_by, caller)`
- `delete_dataset(self, dataset_id)`
- `delete_table(self, table_id)`
- `exists_table(self, table_id)`
- `generate_bigquery_schema_from_df(self, df, specific_types)`
- `incremental_insert_with_deduplication(self, table_id, df, id_cols)`
- `read_table_as_df(self, table_id)`
- `sql2df(self, query)`
- `update_table(self, table_id, df, id_cols)`
- `upload_df_to_table(self, table_id, df)`

<!-- BIGQUERYHELPER END -->


### GoogleBucketHelper

<!-- GOOGLEBUCKETHELPER START -->
- `download_as_text(self, bucket_name, path)`
- `exists_bucket(self, bucket_name)`
- `upload_content(self, content, bucket_name, filename, content_type)`

<!-- GOOGLEBUCKETHELPER END -->

### SecretManagerHelper

<!-- SECRETMANAGERHELPER START -->
- `get_secret(self, project_id, secret_id)`

<!-- SECRETMANAGERHELPER END -->

## Development

When new functions are added run `uv run update_readme.py` to update the README.md file.

## Testing

To run the tests, execute the following command:

```
uv run pytest
```

## Build and Publish

To build and publish the package to PyPI, execute the following command:

```
uv build
uv publish --token <pypi-token>
```
