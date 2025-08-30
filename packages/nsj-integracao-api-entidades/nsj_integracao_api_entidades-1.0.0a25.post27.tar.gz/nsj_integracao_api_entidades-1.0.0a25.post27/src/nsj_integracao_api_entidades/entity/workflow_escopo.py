
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.escopo",
    pk_field="escopoworkflow",
    default_order_fields=["escopoworkflow"],
)
class EscopoEntity(EntityBase):
    escopoworkflow: int = None
    tenant: int = None
    nome: str = None
    codigo: str = None
    lastupdate: datetime.datetime = None
