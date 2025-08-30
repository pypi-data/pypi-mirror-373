
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.segmentosatuacao",
    pk_field="segmentoatuacao",
    default_order_fields=["codigo"],
)
class SegmentosatuacaoEntity(EntityBase):
    segmentoatuacao: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    id_grupoempresarial: uuid.UUID = None
    created_by: dict = None
    updated_by: dict = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    volume_minimo: int = None
