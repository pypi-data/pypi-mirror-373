
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.familias",
    pk_field="familia",
    default_order_fields=["codigo"],
)
class FamiliaEntity(EntityBase):
    familia: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
