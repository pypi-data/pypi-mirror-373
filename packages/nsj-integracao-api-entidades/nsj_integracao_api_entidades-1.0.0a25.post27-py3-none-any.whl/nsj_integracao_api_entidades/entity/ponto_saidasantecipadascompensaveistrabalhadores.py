
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.saidasantecipadascompensaveistrabalhadores",
    pk_field="saidaantecipadacompensaveltrabalhador",
    default_order_fields=["saidaantecipadacompensaveltrabalhador"],
)
class SaidasantecipadascompensaveistrabalhadoreEntity(EntityBase):
    saidaantecipadacompensaveltrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
