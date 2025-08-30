
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.perfiltrib_fed_validades",
    pk_field="perfiltrib_fed_validade",
    default_order_fields=["perfiltrib_fed_validade"],
)
class PerfiltribFedValidadeEntity(EntityBase):
    perfiltrib_fed_validade: uuid.UUID = None
    tenant: int = None
    perfiltrib_fed: uuid.UUID = None
    data: datetime.datetime = None
    lastupdate: datetime.datetime = None
