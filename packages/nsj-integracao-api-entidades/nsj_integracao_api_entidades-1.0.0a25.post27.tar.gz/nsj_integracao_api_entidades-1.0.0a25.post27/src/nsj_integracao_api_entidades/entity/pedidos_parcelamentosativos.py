
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.parcelamentosativos",
    pk_field="parcelamentoativo",
    default_order_fields=["parcelamentoativo"],
)
class ParcelamentosativoEntity(EntityBase):
    parcelamentoativo: uuid.UUID = None
    tenant: int = None
    parcelamento: uuid.UUID = None
    sempre_exibir: bool = None
