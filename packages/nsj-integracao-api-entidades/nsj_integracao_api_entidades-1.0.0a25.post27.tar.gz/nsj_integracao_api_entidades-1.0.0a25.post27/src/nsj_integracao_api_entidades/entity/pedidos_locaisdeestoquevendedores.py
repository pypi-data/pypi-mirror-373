
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.locaisdeestoquevendedores",
    pk_field="localdeestoquevendedores",
    default_order_fields=["localdeestoquevendedores"],
)
class LocaisdeestoquevendedoreEntity(EntityBase):
    tenant: int = None
    localdeestoquevendedores: uuid.UUID = None
    localdeestoque: uuid.UUID = None
    vendedor: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
