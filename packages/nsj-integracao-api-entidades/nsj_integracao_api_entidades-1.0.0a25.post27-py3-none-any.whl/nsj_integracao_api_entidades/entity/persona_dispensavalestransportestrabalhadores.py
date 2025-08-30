
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.dispensavalestransportestrabalhadores",
    pk_field="dispensavaletransportetrabalhador",
    default_order_fields=["dispensavaletransportetrabalhador"],
)
class DispensavalestransportestrabalhadoreEntity(EntityBase):
    dispensavaletransportetrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    datainicio: datetime.datetime = None
    datafim: datetime.datetime = None
    observacao: str = None
    lastupdate: datetime.datetime = None
