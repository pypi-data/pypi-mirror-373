
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.configuracoesordemcalculomovimentosponto",
    pk_field="configuracaoordemcalculomovimentoponto",
    default_order_fields=["configuracaoordemcalculomovimentoponto"],
)
class ConfiguracoesordemcalculomovimentospontoEntity(EntityBase):
    configuracaoordemcalculomovimentoponto: uuid.UUID = None
    tenant: int = None
    empresa: uuid.UUID = None
    tipomovimento: int = None
    ordemcalculomovimento: int = None
    lastupdate: datetime.datetime = None
