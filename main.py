import jira_api
import bigquery
import datadotworld as dw
import logging
import datadotworld_api
from datetime import date
from config import config, config_file_paths


def main():
    # Adds ticket metadata to a local staging CSV
    jira_api.get_jira_tickets()

    # Upload the staging CSV file to BigQuery
    bigquery.upload_to_bigquery(config_file_paths.csv_file, config.table_id)

    # Auto syncs dataset on data.world for real time visibility
    datadotworld_api.sync_datadotworld()


if __name__ == '__main__':
    main()
