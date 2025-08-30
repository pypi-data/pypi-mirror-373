
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.parcelamentos",
    pk_field="parcelamento",
    default_order_fields=["parcelamento"],
)
class ParcelamentoEntity(EntityBase):
    parcelamento: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    incluirissprimeiraparcela: int = None
    intervaloexatoentrevencimentos: int = None
    quantidadeparcelas: int = None
    percentualjuros: float = None
    lastupdate: datetime.datetime = None
    valorminimoparautilizarparcelamento: float = None
    exigirvalorminimoparautilizarparcelamento: bool = None
