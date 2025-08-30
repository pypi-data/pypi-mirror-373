
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.conjuntos",
    pk_field="conjunto",
    default_order_fields=["descricao"],
)
class ConjuntoEntity(EntityBase):
    conjunto: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    cadastro: int = None
    lastupdate: datetime.datetime = None
    codigo: str = None
