
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.configuracoesbancarias",
    pk_field="configuracaobancaria",
    default_order_fields=["nome"],
)
class ConfiguracoesbancariaEntity(EntityBase):
    configuracaobancaria: uuid.UUID = None
    tenant: int = None
    nome: str = None
    valor: str = None
    layoutcobranca: uuid.UUID = None
    layoutpagamento: uuid.UUID = None
    lastupdate: datetime.datetime = None
