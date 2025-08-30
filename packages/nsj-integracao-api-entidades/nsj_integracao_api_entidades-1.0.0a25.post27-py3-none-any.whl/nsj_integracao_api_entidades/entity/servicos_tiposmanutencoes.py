
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.tiposmanutencoes",
    pk_field="tipomanutencao",
    default_order_fields=["descricao"],
)
class TiposmanutencoEntity(EntityBase):
    tipomanutencao: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    ativo: bool = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    codigo: str = None
