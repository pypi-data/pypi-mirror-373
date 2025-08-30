
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.movimentosponto",
    pk_field="movimentoponto",
    default_order_fields=["movimentoponto"],
)
class MovimentospontoEntity(EntityBase):
    movimentoponto: uuid.UUID = None
    tenant: int = None
    tipo: int = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    departamento: uuid.UUID = None
    lotacao: uuid.UUID = None
    rubricaponto: uuid.UUID = None
    sindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
    ordem: int = None
