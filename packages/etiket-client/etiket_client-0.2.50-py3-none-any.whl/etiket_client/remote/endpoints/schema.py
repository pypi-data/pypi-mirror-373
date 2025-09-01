from etiket_client.remote.client import client
from etiket_client.remote.endpoints.models.schema import SchemaReadWithScopes

import typing, uuid

def schema_read(schema_uuid : uuid.UUID) -> SchemaReadWithScopes:
    response = client.get("/schema/", params={"schema_uuid":schema_uuid})
    return SchemaReadWithScopes.model_validate(response)


def schema_read_many(name_query : str = None, offset = 0, limit = None) -> typing.List[SchemaReadWithScopes]:
    response = client.get("/schemas/", params={"name":name_query,
                            "offset": offset, "limit":limit})
    return [SchemaReadWithScopes.model_validate(schema) for schema in response]
