
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.produtos_faixas_precos_segmentos",
    pk_field="produto_faixa_preco_segmento",
    default_order_fields=["produto_faixa_preco_segmento"],
)
class ProdutoFaixaPrecoSegmentoEntity(EntityBase):
    produto_faixa_preco_segmento: uuid.UUID = None
    tenant: int = None
    produto_faixa_preco_vigencia: uuid.UUID = None
    segmento: uuid.UUID = None
