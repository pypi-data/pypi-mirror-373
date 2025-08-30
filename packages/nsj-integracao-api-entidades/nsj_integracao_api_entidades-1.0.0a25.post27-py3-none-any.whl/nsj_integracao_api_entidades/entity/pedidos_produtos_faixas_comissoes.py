
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.produtos_faixas_comissoes",
    pk_field="produto_faixa_comissao",
    default_order_fields=["produto_faixa_comissao"],
)
class ProdutoFaixaComissoEntity(EntityBase):
    produto_faixa_comissao: uuid.UUID = None
    tenant: int = None
    produto: uuid.UUID = None
    preco_inferior: float = None
    preco_superior: float = None
    percentual: float = None
    qualificacao: int = None
