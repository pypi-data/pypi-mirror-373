
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.tiposfollowups",
    pk_field="tipofollowup",
    default_order_fields=["codigo"],
)
class TiposfollowupEntity(EntityBase):
    tipofollowup: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    ativo: bool = None
    lastupdate: datetime.datetime = None
