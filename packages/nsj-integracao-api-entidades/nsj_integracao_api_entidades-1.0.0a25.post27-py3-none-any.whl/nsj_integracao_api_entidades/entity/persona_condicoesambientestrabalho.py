
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.condicoesambientestrabalho",
    pk_field="condicaoambientetrabalho",
    default_order_fields=["codigo"],
)
class CondicoesambientestrabalhoEntity(EntityBase):
    condicaoambientetrabalho: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    empresa: uuid.UUID = None
    ambiente: uuid.UUID = None
    atividades: str = None
    observacoescomplementares: str = None
    lastupdate: datetime.datetime = None
