
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.midiasorigem",
    pk_field="midiaorigem",
    default_order_fields=["midiaorigem"],
)
class MidiasorigemEntity(EntityBase):
    midiaorigem: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    bloqueado: int = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
    id_grupoempresarial: uuid.UUID = None
