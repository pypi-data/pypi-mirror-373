
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.pendenciaspagamentos",
    pk_field="pendenciapagamento",
    default_order_fields=["pendenciapagamento"],
)
class PendenciaspagamentoEntity(EntityBase):
    pendenciapagamento: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    avisoferiastrabalhador: uuid.UUID = None
    valor: float = None
    consideradonasbases: bool = None
    tipocalculo: int = None
    mes: int = None
    ano: int = None
    pago: bool = None
    origem: int = None
    reajustesindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
