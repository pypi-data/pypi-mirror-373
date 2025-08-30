
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.tiposservicos",
    pk_field="tiposervico",
    default_order_fields=["codigo"],
)
class TiposservicoEntity(EntityBase):
    tiposervico: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    id_grupoempresarial: uuid.UUID = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
