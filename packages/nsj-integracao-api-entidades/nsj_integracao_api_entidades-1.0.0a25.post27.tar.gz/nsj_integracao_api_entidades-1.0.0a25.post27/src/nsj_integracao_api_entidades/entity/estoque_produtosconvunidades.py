
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.produtosconvunidades",
    pk_field="produtoconvunidade",
    default_order_fields=["produtoconvunidade"],
)
class ProdutosconvunidadeEntity(EntityBase):
    produtoconvunidade: uuid.UUID = None
    tenant: int = None
    produto: uuid.UUID = None
    id_grupo: uuid.UUID = None
    razao: float = None
    unidadepadrao: uuid.UUID = None
    unidade: uuid.UUID = None
    lastupdate: datetime.datetime = None
    codigoalternativo: str = None
