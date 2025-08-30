
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.processosrubricas",
    pk_field="processorubrica",
    default_order_fields=["processorubrica"],
)
class ProcessosrubricaEntity(EntityBase):
    processorubrica: uuid.UUID = None
    tenant: int = None
    processo: uuid.UUID = None
    rubrica: uuid.UUID = None
    lastupdate: datetime.datetime = None
