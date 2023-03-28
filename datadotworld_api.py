import datadotworld as dw
import logging


def sync_datadotworld():
    client = dw.api_client()
    client.sync_files('jcorg/all-dws-tickets')
    logging.info(f"Sync pushed to data.world")


    