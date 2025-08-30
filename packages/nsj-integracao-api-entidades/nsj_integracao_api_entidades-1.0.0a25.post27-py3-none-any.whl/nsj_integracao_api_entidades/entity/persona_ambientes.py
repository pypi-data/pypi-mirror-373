
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.ambientes",
    pk_field="ambiente",
    default_order_fields=["codigo"],
)
class AmbienteEntity(EntityBase):
    ambiente: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipo: int = None
    tomador: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    obra: uuid.UUID = None
    empresa: uuid.UUID = None
    lastupdate: datetime.datetime = None
    nome: str = None
    lotacao: uuid.UUID = None
