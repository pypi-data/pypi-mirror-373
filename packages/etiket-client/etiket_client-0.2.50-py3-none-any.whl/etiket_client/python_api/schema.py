from etiket_client.local.dao.schema import dao_schema, SchemaRead
from etiket_client.local.dao.scope import dao_scope

from etiket_client.local.database import Session

from etiket_client.settings.user_settings import user_settings


def get_current_schema() -> SchemaRead:
    # TODO sync scopes
    with Session() as session:
        return dao_scope.read(user_settings.current_scope, session)._schema

def validate_schema(schema_uuid, dataset) -> bool:
    pass
