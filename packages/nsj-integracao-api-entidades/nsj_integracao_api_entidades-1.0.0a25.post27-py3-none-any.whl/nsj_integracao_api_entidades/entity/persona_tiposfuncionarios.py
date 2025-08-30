
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tiposfuncionarios",
    pk_field="tipofuncionario",
    default_order_fields=["codigo"],
)
class TiposfuncionarioEntity(EntityBase):
    tipofuncionario: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    empresa: uuid.UUID = None
    lastupdate: datetime.datetime = None
