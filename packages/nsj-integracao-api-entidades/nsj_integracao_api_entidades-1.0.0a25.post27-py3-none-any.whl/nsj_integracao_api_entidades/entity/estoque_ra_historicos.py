
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.ra_historicos",
    pk_field="ra_historico",
    default_order_fields=["historico"],
)
class RaHistoricoEntity(EntityBase):
    ra_historico: uuid.UUID = None
    tenant: int = None
    ra: uuid.UUID = None
    data: datetime.datetime = None
    origem: int = None
    usuario: uuid.UUID = None
    historico: str = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    created_by: dict = None
    contanasajon: str = None
