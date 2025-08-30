
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.perfiltrib_est_validades",
    pk_field="perfiltrib_est_validade",
    default_order_fields=["perfiltrib_est_validade"],
)
class PerfiltribEstValidadeEntity(EntityBase):
    perfiltrib_est_validade: uuid.UUID = None
    tenant: int = None
    perfiltrib_est: uuid.UUID = None
    data: datetime.datetime = None
    lastupdate: datetime.datetime = None
