
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.conjuntosfichas",
    pk_field="conjuntoficha",
    default_order_fields=["conjuntoficha"],
)
class ConjuntosfichaEntity(EntityBase):
    conjuntoficha: uuid.UUID = None
    tenant: int = None
    registro: uuid.UUID = None
    conjunto: uuid.UUID = None
    lastupdate: datetime.datetime = None
