
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.formasdepagamentosativas",
    pk_field="formadepagamentoativa",
    default_order_fields=["formadepagamentoativa"],
)
class FormasdepagamentosativaEntity(EntityBase):
    formadepagamentoativa: uuid.UUID = None
    tenant: int = None
    formapagamento: uuid.UUID = None
