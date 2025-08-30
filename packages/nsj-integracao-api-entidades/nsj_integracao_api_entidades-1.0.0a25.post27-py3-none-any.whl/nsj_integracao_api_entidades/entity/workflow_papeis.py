
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.papeis",
    pk_field="papel",
    default_order_fields=["papel"],
)
class PapeiEntity(EntityBase):
    papel: uuid.UUID = None
    tenant: int = None
    diagrama: uuid.UUID = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    canstartworkflow: bool = None
    escopoworkflow: int = None
