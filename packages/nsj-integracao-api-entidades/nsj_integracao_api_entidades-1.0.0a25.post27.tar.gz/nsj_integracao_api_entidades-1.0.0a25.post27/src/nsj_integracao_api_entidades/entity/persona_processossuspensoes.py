
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.processossuspensoes",
    pk_field="processosuspensao",
    default_order_fields=["codigo"],
)
class ProcessossuspensoEntity(EntityBase):
    processosuspensao: uuid.UUID = None
    tenant: int = None
    processo: uuid.UUID = None
    codigo: str = None
    tipo: int = None
    datadecisao: datetime.datetime = None
    depositointegral: bool = None
    extensaodecisao: int = None
    lastupdate: datetime.datetime = None
