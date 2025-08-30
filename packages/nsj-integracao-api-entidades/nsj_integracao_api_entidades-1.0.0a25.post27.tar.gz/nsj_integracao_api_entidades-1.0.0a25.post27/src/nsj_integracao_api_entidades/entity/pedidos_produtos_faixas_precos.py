
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.produtos_faixas_precos",
    pk_field="produto_faixa_preco",
    default_order_fields=["produto_faixa_preco"],
)
class ProdutoFaixaPrecoEntity(EntityBase):
    produto_faixa_preco: uuid.UUID = None
    tenant: int = None
    produto_faixa_preco_vigencia: uuid.UUID = None
    tipo: int = None
    preco_inferior: float = None
    preco_superior: float = None
    quantidade_minima: float = None
    percentual: float = None
