
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.intervalosjornadas",
    pk_field="intervalojornada",
    default_order_fields=["intervalojornada"],
)
class IntervalosjornadaEntity(EntityBase):
    intervalojornada: uuid.UUID = None
    tenant: int = None
    inicio: datetime.time = None
    fim: datetime.time = None
    jornada: uuid.UUID = None
    lastupdate: datetime.datetime = None
