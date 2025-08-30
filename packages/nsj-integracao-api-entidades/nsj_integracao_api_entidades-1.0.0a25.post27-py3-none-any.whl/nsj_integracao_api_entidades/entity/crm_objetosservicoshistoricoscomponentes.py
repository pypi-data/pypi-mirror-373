
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.objetosservicoshistoricoscomponentes",
    pk_field="objetoservicohistoricocomponente",
    default_order_fields=["objetoservicohistoricocomponente"],
)
class ObjetosservicoshistoricoscomponenteEntity(EntityBase):
    objetoservicohistoricocomponente: uuid.UUID = None
    tenant: int = None
    id_objetoservicohistoricooferta: uuid.UUID = None
    id_componente: uuid.UUID = None
    data: datetime.datetime = None
    ativa: bool = None
    lastupdate: datetime.datetime = None
    quantidade: float = None
    id_documento_item: uuid.UUID = None
