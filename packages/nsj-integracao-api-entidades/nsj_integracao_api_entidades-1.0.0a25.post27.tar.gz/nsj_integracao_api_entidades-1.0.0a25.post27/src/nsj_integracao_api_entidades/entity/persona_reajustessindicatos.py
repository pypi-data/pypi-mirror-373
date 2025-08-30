
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.reajustessindicatos",
    pk_field="reajustesindicato",
    default_order_fields=["reajustesindicato"],
)
class ReajustessindicatoEntity(EntityBase):
    reajustesindicato: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    descricao: str = None
    percentual: float = None
    tipo: int = None
    datadeveriatersidoconcedido: datetime.datetime = None
    sindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
