import os
from datetime import datetime
from google.cloud import bigquery


def upload_to_bigquery(csv_file, table_id):

    # Creates a BigQuery client object and initializes the job
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False
    )

    # Sets the BigQuery table schema
    schema = [
        bigquery.SchemaField("issue_key", "STRING"),
        bigquery.SchemaField("link", "STRING"),
        bigquery.SchemaField("summary", "STRING"),
        bigquery.SchemaField("issue_status", "STRING"),
        bigquery.SchemaField("assignee", "STRING"),
        bigquery.SchemaField("organization", "STRING"),
        bigquery.SchemaField("customer", "STRING"),
        bigquery.SchemaField("start_time", "TIMESTAMP"),
        bigquery.SchemaField("stop_time", "TIMESTAMP"),
        bigquery.SchemaField("breach_time", "TIMESTAMP"),
        bigquery.SchemaField("breached", "BOOL"),
        bigquery.SchemaField("elapsed_time", "NUMERIC"),
        bigquery.SchemaField("remaining_time", "NUMERIC"),
        bigquery.SchemaField("need_followup", "STRING"),
        bigquery.SchemaField("module", "STRING"),
        bigquery.SchemaField("sub_status", "STRING"),
        bigquery.SchemaField("request_type", "STRING"),
        bigquery.SchemaField("created_date", "TIMESTAMP"),
        bigquery.SchemaField("resolution_date", "TIMESTAMP"),
        bigquery.SchemaField("dw_priority", "STRING"),
        bigquery.SchemaField("dw_severity", "STRING"),
        bigquery.SchemaField("last_customer_comment_date", "TIMESTAMP"),
        bigquery.SchemaField("last_customer_comment_author", "STRING"),
        bigquery.SchemaField("last_support_comment_date", "TIMESTAMP"),
        bigquery.SchemaField("last_support_comment_author", "STRING"),
        bigquery.SchemaField("updated", "STRING")
    ]

    # Checks if table exists
    if table_exists(client, table_id):
        delete_query = f"DELETE FROM {table_id} WHERE True"
        client.query(delete_query)

        # Using local staging CSV to load
        with open(csv_file, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        print_load_results(job, client, table_id)

    else:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)

        # Using local staging CSV to load
        with open(csv_file, "rb") as source_file:
            job = client.load_table_from_file(source_file, table_id, job_config=job_config)

        print_load_results(job, client, table_id)


def table_exists(client, table_id):
    from google.cloud.exceptions import NotFound
    try:
        client.get_table(table_id)
        return True
    except NotFound:
        return False


def print_load_results(job, client, table_id):
    job.result()
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")