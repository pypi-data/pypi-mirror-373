
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.romaneios_entregadores",
    pk_field="romaneio_entregador",
    default_order_fields=["romaneio_entregador"],
)
class RomaneioEntregadoreEntity(EntityBase):
    romaneio_entregador: uuid.UUID = None
    tenant: int = None
    romaneio: uuid.UUID = None
    entregador: uuid.UUID = None
