
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.escalasfolgastrabalhadores",
    pk_field="escalafolgatrabalhador",
    default_order_fields=["escalafolgatrabalhador"],
)
class EscalasfolgastrabalhadoreEntity(EntityBase):
    escalafolgatrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    trabalhador: uuid.UUID = None
    horario: uuid.UUID = None
    lastupdate: datetime.datetime = None
