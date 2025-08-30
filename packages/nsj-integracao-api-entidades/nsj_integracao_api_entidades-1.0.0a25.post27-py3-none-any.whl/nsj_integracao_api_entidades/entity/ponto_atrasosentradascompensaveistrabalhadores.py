
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.atrasosentradascompensaveistrabalhadores",
    pk_field="atrasoentradacompensaveltrabalhador",
    default_order_fields=["atrasoentradacompensaveltrabalhador"],
)
class AtrasosentradascompensaveistrabalhadoreEntity(EntityBase):
    atrasoentradacompensaveltrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
