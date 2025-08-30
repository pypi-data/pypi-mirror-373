
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.diascompensacoestrabalhadores",
    pk_field="diacompensacaotrabalhador",
    default_order_fields=["diacompensacaotrabalhador"],
)
class DiascompensacoestrabalhadoreEntity(EntityBase):
    diacompensacaotrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    trabalhador: uuid.UUID = None
    horario: uuid.UUID = None
    lastupdate: datetime.datetime = None
