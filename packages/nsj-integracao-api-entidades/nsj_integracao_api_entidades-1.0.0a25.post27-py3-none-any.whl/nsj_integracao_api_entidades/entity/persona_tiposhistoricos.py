
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tiposhistoricos",
    pk_field="tipohistorico",
    default_order_fields=["tipohistorico"],
)
class TiposhistoricoEntity(EntityBase):
    tipohistorico: str = None
    tenant: int = None
    descricao: str = None
    grupo: int = None
    subgrupo: int = None
    codigo: str = None
    lastupdate: datetime.datetime = None
