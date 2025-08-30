
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.convocacoestrabalhadores",
    pk_field="convocacaotrabalhador",
    default_order_fields=["trabalhador"],
)
class ConvocacoestrabalhadoreEntity(EntityBase):
    convocacaotrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    lotacao: uuid.UUID = None
    horario: uuid.UUID = None
    datainicial: datetime.datetime = None
    datafinal: datetime.datetime = None
    descricao: str = None
    lastupdate: datetime.datetime = None
