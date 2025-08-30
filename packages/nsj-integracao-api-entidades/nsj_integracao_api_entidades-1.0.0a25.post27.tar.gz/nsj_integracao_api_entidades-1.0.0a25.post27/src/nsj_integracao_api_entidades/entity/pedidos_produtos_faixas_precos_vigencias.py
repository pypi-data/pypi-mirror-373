
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.produtos_faixas_precos_vigencias",
    pk_field="produto_faixa_preco_vigencia",
    default_order_fields=["produto_faixa_preco_vigencia"],
)
class ProdutoFaixaPrecoVigenciaEntity(EntityBase):
    produto_faixa_preco_vigencia: uuid.UUID = None
    tenant: int = None
    produto: uuid.UUID = None
    data_inicio: datetime.datetime = None
    data_fim: datetime.datetime = None
    qualificacao: int = None
