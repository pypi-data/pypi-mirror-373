
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.negociacoesvalores",
    pk_field="negociacaovalor",
    default_order_fields=["negociacaovalor"],
)
class NegociacoesvaloreEntity(EntityBase):
    negociacaovalor: uuid.UUID = None
    tenant: int = None
    negociacaofornecedor: uuid.UUID = None
    negociacaoitem: uuid.UUID = None
    negociacao: uuid.UUID = None
    valorcotado: float = None
    quantidadedisponivel: float = None
    quantidadedesejada: float = None
    lastupdate: datetime.datetime = None
