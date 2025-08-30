
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.propostascotacoes",
    pk_field="propostacotacao",
    default_order_fields=["referencia"],
)
class PropostascotacoEntity(EntityBase):
    propostacotacao: uuid.UUID = None
    tenant: int = None
    fornecedor: uuid.UUID = None
    requisicaocompra: uuid.UUID = None
    valorfrete: float = None
    outrasdespesas: float = None
    prazoentrega: int = None
    observacao: str = None
    dataproposta: datetime.datetime = None
    estabelecimento: uuid.UUID = None
    lastupdate: datetime.datetime = None
    referencia: str = None
    pis: float = None
    cofins: float = None
    icms: float = None
    icmsst: float = None
    ipi: float = None
