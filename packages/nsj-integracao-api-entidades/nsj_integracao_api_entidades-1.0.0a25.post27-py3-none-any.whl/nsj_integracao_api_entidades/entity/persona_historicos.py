
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.historicos",
    pk_field="historico",
    default_order_fields=["historico"],
)
class HistoricoEntity(EntityBase):
    historico: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    tipohistorico: str = None
    lastupdate: datetime.datetime = None
