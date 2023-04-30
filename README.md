# jira-ticket-metrics

# Purpose
The jira-ticket-metrics app is designed to provide advanced analytic capabilities of customer and team metrics, relating to volume, resolution time, response time, customer experience, service governance, and other key metrics. It serves as an extension to the current reporting capabilities of JIRA by providing a more flexible manner of visualization and reporting.

# How it Works
The app uses a combination of JIRA, BigQuery, pandas, and data.world APIs to collect and store data, generate visualizations, and maintain real-time updates across the pipeline. Here's an overview of how it works:

1. On initial ingest, the script grabs all tickets from the beginning of the year.
2. A cron automated script begins to run daily, grabbing tickets that were 'updated' in the last 48 hours and appends to the 'all_dws_tickets' table, or updates tickets that already exist in this table based on the ticket's 'issue_key'.
3. The local CSV is then uploaded to a BigQuery table and connected to data.world via the Connection Manager.
4. Finally, the script calls to data.world to force a sync on each run to maintain real-time updates across the pipeline.

One of the key features of the app is API chaining (limited to 100 per minute). Each ticket grabs customer and support metadata, including the author and date of the latest comment.

# Installation
Currently, this jira-ticket-metrics app is not available for installation as it requires local configurations and access to JIRA, BigQuery, and data.world resources.

However, the Python Packages required are listed in the 'requirements.txt' file and can be installed after cloning by running ```pip install -r requirements.txt``` in the root directory.


# Documentation
JIRA API documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/  
BigQuery documentation: https://cloud.google.com/bigquery/docs/  
data.world documentation: https://docs.data.world/
