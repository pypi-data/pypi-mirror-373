
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_fretes",
    pk_field="df_frete",
    default_order_fields=["df_frete"],
)
class DfFreteEntity(EntityBase):
    df_frete: uuid.UUID = None
    tenant: int = None
    id_docfis: uuid.UUID = None
    ibgeocorrenciafatorgeradoricms: str = None
    id_transportadora: uuid.UUID = None
    modalidade: int = None
    valorservico: float = None
    valorbcretencaoicms: float = None
    parcelaicmsretido: float = None
    valoricmsretido: float = None
    cfopservicotransporte: str = None
    placaveiculo: str = None
    ufveiculo: str = None
    rntcveiculo: str = None
    vagao: str = None
    balsa: str = None
    lastupdate: datetime.datetime = None
    id_veiculo: uuid.UUID = None
    tiporateio: int = None
