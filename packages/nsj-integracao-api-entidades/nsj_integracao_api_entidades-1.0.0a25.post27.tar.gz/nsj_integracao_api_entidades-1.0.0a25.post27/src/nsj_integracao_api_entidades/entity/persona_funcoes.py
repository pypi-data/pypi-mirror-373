
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.funcoes",
    pk_field="funcao",
    default_order_fields=["codigo"],
)
class FuncoEntity(EntityBase):
    funcao: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    empresa: uuid.UUID = None
    cbo: str = None
    lastupdate: datetime.datetime = None
