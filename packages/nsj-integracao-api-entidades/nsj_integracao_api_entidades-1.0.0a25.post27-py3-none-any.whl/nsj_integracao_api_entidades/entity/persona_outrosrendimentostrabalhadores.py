
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.outrosrendimentostrabalhadores",
    pk_field="outrorendimentotrabalhador",
    default_order_fields=["outrorendimentotrabalhador"],
)
class OutrosrendimentostrabalhadoreEntity(EntityBase):
    outrorendimentotrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    valor: float = None
    evento: uuid.UUID = None
    lastupdate: datetime.datetime = None
