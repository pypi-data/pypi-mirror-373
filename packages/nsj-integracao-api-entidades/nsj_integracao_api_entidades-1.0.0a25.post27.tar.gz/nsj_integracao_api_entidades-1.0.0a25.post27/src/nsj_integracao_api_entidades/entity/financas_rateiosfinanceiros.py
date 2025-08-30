
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.rateiosfinanceiros",
    pk_field="rateiofinanceiro",
    default_order_fields=["rateiofinanceiro"],
)
class RateiosfinanceiroEntity(EntityBase):
    rateiofinanceiro: uuid.UUID = None
    tenant: int = None
    valor: float = None
    centrocusto: uuid.UUID = None
    classificacaofinanceira: uuid.UUID = None
    documentorateado: uuid.UUID = None
    lastupdate: datetime.datetime = None
    projeto: uuid.UUID = None
    itemcontrato: uuid.UUID = None
    discriminacao: str = None
    percentual: float = None
    bempatrimonial: uuid.UUID = None
    criacaoautomatica: bool = None
    idrateiofinanceiroorigem: uuid.UUID = None
    id_estabelecimento_reembolso: uuid.UUID = None
