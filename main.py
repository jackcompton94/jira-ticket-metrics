import jira_api
import datadotworld as dw

jira_api.get_jira_tickets()

# Auto syncs dataset on data.world for real time visibility
client = dw.api_client()
client.sync_files('jcorg/all-dws-tickets')
