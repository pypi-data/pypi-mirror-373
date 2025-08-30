
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.categoriasdeprodutos",
    pk_field="categoriadeproduto",
    default_order_fields=["codigo"],
)
class CategoriasdeprodutoEntity(EntityBase):
    categoriadeproduto: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    completarcodigoproduto: bool = None
    sigla: str = None
    categoriasuperior: uuid.UUID = None
    figuratributaria: uuid.UUID = None
    ncm: uuid.UUID = None
    controlaestoque: bool = None
    quantidademinima: float = None
    quantidademaxima: float = None
    quantidadealerta: float = None
    dimensaohorizontal: uuid.UUID = None
    dimensaovertical: uuid.UUID = None
    classificacaofinanceira_compra: uuid.UUID = None
    classificacaofinanceira_venda: uuid.UUID = None
    lastupdate: datetime.datetime = None
    classificacaofinanceiracompra: uuid.UUID = None
    classificacaofinanceiravenda: uuid.UUID = None
    lead_time: int = None
