from fairo.core.client.client import BaseClient


def get_resource_by_id(client: BaseClient, resource_id: str):
    try:
        response = client.get(f'/resources/{resource_id}')
        return response
    except Exception as e:
        raise e