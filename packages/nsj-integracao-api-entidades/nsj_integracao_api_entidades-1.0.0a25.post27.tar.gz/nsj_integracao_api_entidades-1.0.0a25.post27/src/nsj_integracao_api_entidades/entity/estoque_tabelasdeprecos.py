
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecos",
    pk_field="tabeladepreco",
    default_order_fields=["codigo"],
)
class TabelasdeprecoEntity(EntityBase):
    tabeladepreco: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    desconto: int = None
    reajuste: float = None
    id_estabelecimento: uuid.UUID = None
    finalidade: int = None
    bloqueada: bool = None
    id_empresa: uuid.UUID = None
    inicioperiodo: datetime.datetime = None
    fimperiodo: datetime.datetime = None
    lastupdate: datetime.datetime = None
    datahoraaplicacaoreajuste: datetime.datetime = None
    dataagendamentoreajuste: datetime.datetime = None
    percentualfatorcomissao: float = None
    descontosobreprecovenda: bool = None
    descontovalorproduto: bool = None
