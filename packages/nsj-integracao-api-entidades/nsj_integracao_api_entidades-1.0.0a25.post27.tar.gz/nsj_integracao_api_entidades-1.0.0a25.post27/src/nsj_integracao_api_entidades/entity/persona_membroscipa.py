
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.membroscipa",
    pk_field="membrocipa",
    default_order_fields=["membrocipa"],
)
class MembroscipaEntity(EntityBase):
    membrocipa: uuid.UUID = None
    tenant: int = None
    empresa: uuid.UUID = None
    trabalhador: uuid.UUID = None
    datainicial: datetime.datetime = None
    datafinal: datetime.datetime = None
    tipo: int = None
    lastupdate: datetime.datetime = None
