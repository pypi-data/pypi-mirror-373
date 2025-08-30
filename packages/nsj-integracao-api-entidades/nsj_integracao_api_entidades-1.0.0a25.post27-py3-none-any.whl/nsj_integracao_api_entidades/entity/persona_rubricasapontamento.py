
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.rubricasapontamento",
    pk_field="rubricaapontamento",
    default_order_fields=["rubricaapontamento"],
)
class RubricasapontamentoEntity(EntityBase):
    rubricaapontamento: uuid.UUID = None
    tenant: int = None
    rubrica: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    ordem: int = None
