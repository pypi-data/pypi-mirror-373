
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.parcelas",
    pk_field="parcela",
    default_order_fields=["parcela"],
)
class ParcelaEntity(EntityBase):
    parcela: uuid.UUID = None
    tenant: int = None
    quantidadediapagamento: int = None
    percentualpagamento: float = None
    parcelamento: uuid.UUID = None
    lastupdate: datetime.datetime = None
