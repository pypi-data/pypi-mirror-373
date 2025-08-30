
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.tiposordensservicos",
    pk_field="tipoordemservico",
    default_order_fields=["descricao"],
)
class TiposordensservicoEntity(EntityBase):
    tipoordemservico: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    codigo: str = None
