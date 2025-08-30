
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_fretes_volumes",
    pk_field="df_frete_volume",
    default_order_fields=["df_frete_volume"],
)
class DfFreteVolumeEntity(EntityBase):
    df_frete_volume: uuid.UUID = None
    tenant: int = None
    id_docfis: uuid.UUID = None
    quantidade: float = None
    especie: str = None
    marca: str = None
    numeracao: str = None
    pesoliquido: float = None
    pesobruto: float = None
    lastupdate: datetime.datetime = None
