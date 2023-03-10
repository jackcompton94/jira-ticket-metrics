def if_table_exists(client, table_id):
    from google.cloud.exceptions import NotFound
    try:
        client.get_table(table_id)
        return True
    except NotFound:
        return False