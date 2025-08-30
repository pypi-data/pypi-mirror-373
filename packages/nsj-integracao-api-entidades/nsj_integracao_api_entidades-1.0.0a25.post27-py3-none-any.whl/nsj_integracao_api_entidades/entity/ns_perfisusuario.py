
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.perfisusuario",
    pk_field="perfilusuario",
    default_order_fields=["nome"],
)
class PerfisusuarioEntity(EntityBase):
    perfilusuario: uuid.UUID = None
    tenant: int = None
    nome: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
