
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.horariosespeciais",
    pk_field="horarioespecial",
    default_order_fields=["horarioespecial"],
)
class HorariosespeciaiEntity(EntityBase):
    horarioespecial: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    horario: uuid.UUID = None
    jornada: uuid.UUID = None
    lastupdate: datetime.datetime = None
