
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.operacoesestabelecimentos",
    pk_field="operacaoestabelecimento",
    default_order_fields=["operacaoestabelecimento"],
)
class OperacoesestabelecimentoEntity(EntityBase):
    operacaoestabelecimento: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    operacao: uuid.UUID = None
    lastupdate: datetime.datetime = None
    considerar_nos_relatorios: bool = None
