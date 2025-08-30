
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.horariosalternativostrabalhadores",
    pk_field="horarioalternativotrabalhador",
    default_order_fields=["horarioalternativotrabalhador"],
)
class HorariosalternativostrabalhadoreEntity(EntityBase):
    horarioalternativotrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    horario: uuid.UUID = None
    lastupdate: datetime.datetime = None
