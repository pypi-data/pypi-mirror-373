
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.classificados",
    pk_field="classificado",
    default_order_fields=["classificado"],
)
class ClassificadoEntity(EntityBase):
    classificado: uuid.UUID = None
    tenant: int = None
    lastupdate: datetime.datetime = None
