
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.itensprocessarcontaspagar",
    pk_field="itemprocessarcontapagar",
    default_order_fields=["itemprocessarcontapagar"],
)
class ItensprocessarcontaspagarEntity(EntityBase):
    itemprocessarcontapagar: uuid.UUID = None
    tenant: int = None
    grupoempresarial: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    tipoacao: int = None
    atc: uuid.UUID = None
    prestador: uuid.UUID = None
    contacorrente: uuid.UUID = None
    contaemprestimo: uuid.UUID = None
    formapagamento: uuid.UUID = None
    vencimento: datetime.datetime = None
    valor: float = None
    titulogerado: uuid.UUID = None
    prestacaogerada: uuid.UUID = None
    tipoprocessamento: int = None
    dataprocessamento: datetime.datetime = None
    motivofalha: str = None
