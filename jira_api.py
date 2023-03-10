import json
from datetime import datetime
import requests
import pandas as pd
import os
import bigquery
from config import config, config_file_paths, config_tokens, config_endpoints
from ratelimit import limits, sleep_and_retry


def get_jira_tickets():
    while True:
        # API Response
        response = requests.get(config_endpoints.search_project_endpoint, headers=config.headers, params=config.query, auth=(config_tokens.USER_NAME, config_tokens.API_TOKEN))

        if response.status_code == 200:
            response_data = response.json()
            issues = response_data['issues']
            total = response_data['total']

            print(f"Ticket total: {total} Current index: {config.query['startAt']}")

            # If the value at which we start our extract from is greater than the total number of tickets exit the loop
            if config.query['startAt'] >= total:
                break

            # Check if the csv has been created
            if os.path.exists(config_file_paths.csv_file):
                # Read existing data from CSV into a DataFrame
                df_existing = pd.read_csv(config_file_paths.csv_file)
            else:
                # If the file doesn't exist, adjust API parameter for first ingest
                config.query['jql'] = f'project=DWS and created >= startOfYear()'

                # Create an empty DataFrame
                df_existing = pd.DataFrame(columns=["issue_key",
                                                    "summary",
                                                    "issue_status",
                                                    "assignee",
                                                    "organization",
                                                    "customer",
                                                    "start_time",
                                                    "stop_time",
                                                    "breach_time",
                                                    "breached",
                                                    "elapsed_time",
                                                    "remaining_time",
                                                    "need_followup",
                                                    "module",
                                                    "sub_status",
                                                    "request_type",
                                                    "created_date",
                                                    "resolution_date",
                                                    "dw_priority",
                                                    "dw_severity",
                                                    "last_customer_comment_date",
                                                    "last_customer_comment_author",
                                                    "last_support_comment_date",
                                                    "last_support_comment_author"])

            # Prepare df_new for all new data
            df_new = pd.DataFrame(columns=["issue_key",
                                           "summary",
                                           "issue_status",
                                           "assignee",
                                           "organization",
                                           "customer",
                                           "start_time",
                                           "stop_time",
                                           "breach_time",
                                           "breached",
                                           "elapsed_time",
                                           "remaining_time",
                                           "need_followup",
                                           "module",
                                           "sub_status",
                                           "request_type",
                                           "created_date",
                                           "resolution_date",
                                           "dw_priority",
                                           "dw_severity",
                                           "last_customer_comment_date",
                                           "last_customer_comment_author",
                                           "last_support_comment_date",
                                           "last_support_comment_author"])

            # Extract the relevant fields
            for issue in issues:
                issue_key = issue['key']
                issue_status = issue['fields']['status']['name']
                summary = issue['fields']['summary']
                time = issue['fields']['customfield_10883']['completedCycles']
                need_followup = issue['fields']['customfield_11095']
                assignee = issue['fields']['assignee']
                customer = issue['fields']['customfield_11075']
                module = issue['fields']['customfield_11103']
                sub_status = issue['fields']['customfield_11101']
                request_type = issue['fields']['customfield_10700']['requestType']['name']
                resolution_date_str = issue['fields']['resolutiondate']
                created_date_str = issue['fields']['created']
                dw_priority = issue['fields']['customfield_11091']
                dw_severity = issue['fields']['customfield_11090']
                organization = issue['fields']['customfield_10600']

                # Checks if SLA is being tracked, if not the values are set to NULL
                if len(time) == 0:
                    start_time = None
                    stop_time = None
                    breach_time = None
                    breached = None
                    elapsed_time = None
                    remaining_time = None
                else:
                    for dict in time:
                        start_time_str = dict['startTime']['iso8601']
                        dt = datetime.strptime(start_time_str[:-5], '%Y-%m-%dT%H:%M:%S')
                        start_time = dt.strftime('%Y-%m-%d %H:%M:%S')

                        stop_time_str = dict['stopTime']['iso8601']
                        dt = datetime.strptime(stop_time_str[:-5], '%Y-%m-%dT%H:%M:%S')
                        stop_time = dt.strftime('%Y-%m-%d %H:%M:%S')

                        breach_time_str = dict['breachTime']['iso8601']
                        dt = datetime.strptime(breach_time_str[:-5], '%Y-%m-%dT%H:%M:%S')
                        breach_time = dt.strftime('%Y-%m-%d %H:%M:%S')

                        breached = bool(dict['breached'])
                        elapsed_time = dict['elapsedTime']['millis']
                        remaining_time = dict['remainingTime']['millis']

                # Checks if Need Followup is set, if not setting to null
                if not bool(need_followup):
                    need_followup = None
                else:
                    need_followup = need_followup['value']

                # Checks if Assignee is set, if not sets to "Unassigned"
                if not bool(assignee):
                    assignee = "unassigned"
                else:
                    assignee = assignee['emailAddress']

                # Checks if Customer Gainsight is set, if not sets to "none"
                if not bool(customer):
                    customer = None
                else:
                    customer = customer[0]['value']

                # Checks if Module is set, if not sets to "none"
                if not bool(module):
                    module = None
                else:
                    module = module['value']

                # Checks if Sub-Status is set, if not sets to "none"
                if not bool(sub_status):
                    sub_status = None
                else:
                    sub_status = sub_status['value']

                # Checks if Created Date is set, if not sets to "none"
                if not bool(created_date_str):
                    created_date = None
                else:
                    dt = datetime.strptime(created_date_str[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    created_date = dt.strftime('%Y-%m-%d %H:%M:%S')

                # Checks if Resolution Date is set, if not sets to "none"
                if not bool(resolution_date_str):
                    resolution_date = None
                else:
                    dt = datetime.strptime(resolution_date_str[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    resolution_date = dt.strftime('%Y-%m-%d %H:%M:%S')

                # Checks if DW Priority is set, if not sets to "none"
                if not bool(dw_priority):
                    dw_priority = None
                else:
                    dw_priority = dw_priority['value']

                # Checks if DW Severity is set, if not sets to "none"
                if not bool(dw_severity):
                    dw_severity = None
                else:
                    dw_severity = dw_severity['value']

                if not bool(organization):
                    organization = None
                else:
                    organization = organization[0]['name']

                # Add more columns here

                comments = get_ticket_comments(issue_key)

                new_data = {'issue_key': issue_key,
                            'summary': summary,
                            'issue_status': issue_status,
                            'assignee': assignee,
                            'organization': organization,
                            'customer': customer,
                            'start_time': start_time,
                            'stop_time': stop_time,
                            'breach_time': breach_time,
                            'breached': breached,
                            'elapsed_time': elapsed_time,
                            'remaining_time': remaining_time,
                            'need_followup': need_followup,
                            'module': module,
                            'sub_status': sub_status,
                            'request_type': request_type,
                            'created_date': created_date,
                            'resolution_date': resolution_date,
                            'dw_priority': dw_priority,
                            'dw_severity': dw_severity,
                            'last_customer_comment_date': comments['last_customer_comment_date'],
                            'last_customer_comment_author': comments['last_customer_comment_author'],
                            'last_support_comment_date': comments['last_support_comment_date'],
                            'last_support_comment_author': comments['last_support_comment_author']}

                new_row = pd.DataFrame(new_data, index=[0])

                df_merged = pd.concat([new_row, df_existing]).drop_duplicates(subset=['issue_key'], keep='last').reset_index(drop=True)

            # Write the merged data back to a CSV file
            df_merged.to_csv(config_file_paths.csv_file, index=False)

            # Upload the staging CSV file to BigQuery
            bigquery.upload_to_bigquery(config_file_paths.csv_file, config.table_id)

            # Add 100 to the index
            config.query['startAt'] += 100

        else:
            print(f'Error: {response.status_code} = {response.reason}')


@sleep_and_retry
@limits(calls=100, period=60)  # allow 100 calls per minute
def get_ticket_comments(issue_key):
    # Comment API Response
    comment_response = requests.get(config_endpoints.comment_endpoint.format(issue_key=issue_key),
                                    headers=config.headers, auth=(
            config_tokens.USER_NAME, config_tokens.API_TOKEN))

    if comment_response.status_code == 200:
        comment_data = comment_response.json()['comments']

        # Lambda Function to get the Last Customer Comment Date and Author
        try:
            last_customer_comment = max(
                (comment for comment in comment_data if comment['author']['accountType'] == 'customer'),
                key=lambda comment: comment['created'])
            last_customer_comment_date_str = last_customer_comment['created']
            last_customer_comment_author = last_customer_comment['author']['emailAddress']

            dt = datetime.strptime(last_customer_comment_date_str[:-5], '%Y-%m-%dT%H:%M:%S.%f')
            last_customer_comment_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            last_customer_comment_date = None
            last_customer_comment_author = None

        # Lambda Function to get the Last Support Comment Date and Author
        try:
            last_support_comment = max((comment for comment in comment_data if
                                        comment['author']['accountType'] == 'atlassian' and comment[
                                            'jsdPublic'] == True), key=lambda comment: comment['created'])
            last_support_comment_date_str = last_support_comment['created']
            last_support_comment_author = last_support_comment['author']['emailAddress']

            dt = datetime.strptime(last_support_comment_date_str[:-5], '%Y-%m-%dT%H:%M:%S.%f')
            last_support_comment_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            last_support_comment_date = None
            last_support_comment_author = None
    else:
        print(f'Error: {comment_response.status_code} = {comment_response.reason}')

    return {'last_customer_comment_date': last_customer_comment_date,
            'last_customer_comment_author': last_customer_comment_author,
            'last_support_comment_date': last_support_comment_date,
            'last_support_comment_author': last_support_comment_author}