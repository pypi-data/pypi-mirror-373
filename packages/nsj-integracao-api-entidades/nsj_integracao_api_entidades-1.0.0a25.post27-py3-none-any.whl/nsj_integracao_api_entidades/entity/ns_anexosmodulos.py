
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.anexosmodulos",
    pk_field="anexomodulo",
    default_order_fields=["arquivo"],
)
class AnexosmoduloEntity(EntityBase):
    anexomodulo: uuid.UUID = None
    tenant: int = None
    arquivo: str = None
    descricao: str = None
    modulodoanexo: int = None
    id_modulodoanexo: uuid.UUID = None
    documentoged: uuid.UUID = None
    lastupdate: datetime.datetime = None
    compartilhado: bool = None
    tipo: int = None
    created_at: datetime.datetime = None
    created_by: dict = None
