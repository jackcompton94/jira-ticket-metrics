import jira_api
import datadotworld as dw
import logging
from datetime import date


def main():
    jira_api.get_jira_tickets()

    # Auto syncs dataset on data.world for real time visibility
    client = dw.api_client()
    client.sync_files('jcorg/all-dws-tickets')
    logging.info(f"Sync pushed to data.world")


if __name__ == '__main__':
    main()
