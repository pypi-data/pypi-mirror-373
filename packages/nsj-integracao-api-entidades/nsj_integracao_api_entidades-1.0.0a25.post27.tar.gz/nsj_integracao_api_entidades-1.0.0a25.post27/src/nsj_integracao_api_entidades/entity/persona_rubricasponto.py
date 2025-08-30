
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.rubricasponto",
    pk_field="rubricaponto",
    default_order_fields=["codigo"],
)
class RubricaspontoEntity(EntityBase):
    rubricaponto: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    evento: uuid.UUID = None
    tipoformula: int = None
    formulabasicacondicao: str = None
    formulabasicavalor: str = None
    formulaavancada: str = None
    empresa: uuid.UUID = None
    tipo: int = None
    lastupdate: datetime.datetime = None
