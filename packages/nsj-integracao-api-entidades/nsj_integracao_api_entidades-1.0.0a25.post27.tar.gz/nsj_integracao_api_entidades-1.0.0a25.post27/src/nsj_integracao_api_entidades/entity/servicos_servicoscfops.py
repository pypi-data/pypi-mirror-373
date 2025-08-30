
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.servicoscfops",
    pk_field="servicocfop",
    default_order_fields=["servicocfop"],
)
class ServicoscfopEntity(EntityBase):
    servicocfop: uuid.UUID = None
    tenant: int = None
    servico_id: uuid.UUID = None
    cfop_id: uuid.UUID = None
    inss_percentual_incidencia: float = None
    inss_percentual_aliquota: float = None
    lastupdate: datetime.datetime = None
