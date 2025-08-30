
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.compensacoeslancamentos",
    pk_field="compensacaolancamento",
    default_order_fields=["compensacaolancamento"],
)
class CompensacoeslancamentoEntity(EntityBase):
    compensacaolancamento: uuid.UUID = None
    tenant: int = None
    lancamentoapuracaoorigem: uuid.UUID = None
    lancamentoapuracaodestino: uuid.UUID = None
    valorlancamentoapuracaoorigem: int = None
    valorlancamentoapuracaodestino: int = None
    lastupdate: datetime.datetime = None
