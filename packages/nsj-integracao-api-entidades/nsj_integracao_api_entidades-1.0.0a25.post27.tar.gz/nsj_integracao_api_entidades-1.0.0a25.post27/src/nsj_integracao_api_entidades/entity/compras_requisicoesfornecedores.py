
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.requisicoesfornecedores",
    pk_field="requisicaofornecedor",
    default_order_fields=["requisicaofornecedor"],
)
class RequisicoesfornecedoreEntity(EntityBase):
    requisicaofornecedor: uuid.UUID = None
    tenant: int = None
    fornecedor: uuid.UUID = None
    requisicaocompra: uuid.UUID = None
    ordem: int = None
    lastupdate: datetime.datetime = None
    solicitacaoenviada: bool = None
