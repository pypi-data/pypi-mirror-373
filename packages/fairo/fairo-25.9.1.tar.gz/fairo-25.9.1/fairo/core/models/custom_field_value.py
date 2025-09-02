from fairo.core.client.client import BaseClient


def get_custom_field_value(client: BaseClient, object_id: str, field_key: str):
    try:
        response = client.get(f'/custom_field_values', params={
            'parent_object_id[]': object_id,
            'custom_field_field_key[]': field_key
        })
        results = response.get('results', [])
        if len(results) > 0:
            return results[0]
        return None
    except Exception as e:
        raise e