
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.historicosadiantamentosavulsos",
    pk_field="historicoadiantamentoavulso",
    default_order_fields=["historicoadiantamentoavulso"],
)
class HistoricosadiantamentosavulsoEntity(EntityBase):
    historicoadiantamentoavulso: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    tipo: int = None
