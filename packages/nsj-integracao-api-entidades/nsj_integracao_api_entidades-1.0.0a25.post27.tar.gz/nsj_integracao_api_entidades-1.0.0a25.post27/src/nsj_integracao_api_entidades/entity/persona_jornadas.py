
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.jornadas",
    pk_field="jornada",
    default_order_fields=["codigo"],
)
class JornadaEntity(EntityBase):
    jornada: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    entrada: datetime.time = None
    saida: datetime.time = None
    tipointervalo: int = None
    duracaointervalo: int = None
    tipojornada: int = None
    descricaotipojornada: str = None
    empresa: uuid.UUID = None
    flexivel: bool = None
    lastupdate: datetime.datetime = None
