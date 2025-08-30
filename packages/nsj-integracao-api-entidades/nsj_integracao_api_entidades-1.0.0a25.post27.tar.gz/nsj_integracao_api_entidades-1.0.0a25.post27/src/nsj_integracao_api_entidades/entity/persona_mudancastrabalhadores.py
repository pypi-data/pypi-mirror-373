
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.mudancastrabalhadores",
    pk_field="mudancatrabalhador",
    default_order_fields=["mudancatrabalhador"],
)
class MudancastrabalhadoreEntity(EntityBase):
    mudancatrabalhador: uuid.UUID = None
    tenant: int = None
    datainicial: datetime.datetime = None
    datafinal: datetime.datetime = None
    tipo: int = None
    simplesconcomitante: str = None
    tipocondicao: str = None
    estabelecimento: uuid.UUID = None
    cargo: uuid.UUID = None
    departamento: uuid.UUID = None
    trabalhador: uuid.UUID = None
    horario: uuid.UUID = None
    lotacao: uuid.UUID = None
    nivelcargo: uuid.UUID = None
    numerohorasmensais: float = None
    funcao: uuid.UUID = None
    lastupdate: datetime.datetime = None
    origem: int = None
