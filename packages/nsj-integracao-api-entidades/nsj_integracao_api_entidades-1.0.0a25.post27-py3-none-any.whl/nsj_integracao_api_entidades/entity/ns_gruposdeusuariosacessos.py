
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.gruposdeusuariosacessos",
    pk_field="grupodeusuarioacesso",
    default_order_fields=["grupodeusuarioacesso"],
)
class GruposdeusuariosacessoEntity(EntityBase):
    grupodeusuarioacesso: uuid.UUID = None
    tenant: int = None
    grupodeusuario: uuid.UUID = None
    tiporegistro: int = None
    registro: uuid.UUID = None
    lastupdate: datetime.datetime = None
