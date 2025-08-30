
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.configuracoesordemcalculomovimentos",
    pk_field="configuracaoordemcalculomovimento",
    default_order_fields=["configuracaoordemcalculomovimento"],
)
class ConfiguracoesordemcalculomovimentoEntity(EntityBase):
    configuracaoordemcalculomovimento: uuid.UUID = None
    tenant: int = None
    empresa: uuid.UUID = None
    tipomovimento: int = None
    ordemcalculomovimento: int = None
    lastupdate: datetime.datetime = None
