
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.contratosclientespartilhas",
    pk_field="contratoclientepartilha",
    default_order_fields=["contratoclientepartilha"],
)
class ContratosclientespartilhaEntity(EntityBase):
    contratoclientepartilha: uuid.UUID = None
    tenant: int = None
    participante: uuid.UUID = None
    contrato: uuid.UUID = None
    participacao: float = None
    pessoamunicipio: uuid.UUID = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    created_by: dict = None
