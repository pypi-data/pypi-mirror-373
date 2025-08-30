
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.objetosservicoshistoricosofertas",
    pk_field="objetoservicohistoricooferta",
    default_order_fields=["objetoservicohistoricooferta"],
)
class ObjetosservicoshistoricosofertaEntity(EntityBase):
    objetoservicohistoricooferta: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    id_oferta: uuid.UUID = None
    id_objetoservico: uuid.UUID = None
    ativa: bool = None
    lastupdate: datetime.datetime = None
    id_objetoservicohistoricooferta_pacote: uuid.UUID = None
    pacote: bool = None
    id_documento_item: uuid.UUID = None
