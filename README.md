# datadotworld-jira-tickets

# Purpose
The datadotworld-ticket-metrics app is designed to provide advanced analysis of customer and team metrics related to volume, resolution time, response time, customer experience, service governance, and other key metrics. It serves as an extension to the current capabilities of JIRA to provide a more efficient manner of providing visualization and reporting.

# How it Works
The app uses a combination of JIRA's API, a local CSV, BigQuery, and data.world to collect and store data, generate visualizations, and maintain real-time updates across the pipeline. Here's an overview of how it works:

1. On initial ingest, the script grabs all tickets from the beginning of the year.
2. A cron automated script begins to run daily, grabbing tickets that were 'updated' in the last 24 hours and appends to the 'all_dws_tickets' table, or updates tickets that already exist based on the 'issue_key'.
3. The local CSV is then uploaded to a BigQuery table and connected to data.world via the Connection Manager.
4. Finally, the script calls to data.world to force a sync on each run to maintain real-time updates across the pipeline.
One of the key features of the app is API chaining (limited to 100 per minute) for each ticket to grab customer and support metadata, including the author and date of the comment.

# Installation
Currently, the datadotworld-ticket-metrics app is not available for installation as it requires custom configuration and access to JIRA, BigQuery, and data.world resources.

However, the source code is available on GitHub and can be used as a reference or starting point for building a similar app.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Documentation
JIRA API documentation: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/  
BigQuery documentation: https://cloud.google.com/bigquery/docs/  
data.world documentation: https://docs.data.world/
