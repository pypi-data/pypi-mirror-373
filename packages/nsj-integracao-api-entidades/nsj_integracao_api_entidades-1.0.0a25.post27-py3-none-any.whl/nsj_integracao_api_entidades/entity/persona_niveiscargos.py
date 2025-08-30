
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.niveiscargos",
    pk_field="nivelcargo",
    default_order_fields=["codigo"],
)
class NiveiscargoEntity(EntityBase):
    nivelcargo: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    data: datetime.datetime = None
    valorsalario: float = None
    valoranterior: float = None
    observacao: str = None
    dataatualizacaoanterior: datetime.datetime = None
    cargo: uuid.UUID = None
    lastupdate: datetime.datetime = None
