from etiket_client.remote.endpoints.models.scope import ScopeRead
from etiket_client.remote.endpoints.models.schema_base import SchemaBase, SchemaRead, SchemaData

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

import uuid

class SchemaCreate(SchemaBase):
    pass

class SchemaReadWithScopes(SchemaRead):
    # scopes : List[ScopeRead]
    pass
    
class SchemaUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name : Optional[str] = Field(default=None)
    description : Optional[str] = Field(default=None)
    schema_ : Optional[SchemaData] = Field(alias='schema', default=None)

class SchemaDelete(BaseModel):
    uuid: uuid.UUID