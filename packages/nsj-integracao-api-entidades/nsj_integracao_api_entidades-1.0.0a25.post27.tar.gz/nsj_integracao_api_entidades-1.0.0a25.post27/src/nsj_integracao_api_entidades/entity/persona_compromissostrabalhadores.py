
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.compromissostrabalhadores",
    pk_field="compromissotrabalhador",
    default_order_fields=["compromissotrabalhador"],
)
class CompromissostrabalhadoreEntity(EntityBase):
    compromissotrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    data: datetime.datetime = None
    descricao: str = None
    abonadiaponto: bool = None
    lastupdate: datetime.datetime = None
