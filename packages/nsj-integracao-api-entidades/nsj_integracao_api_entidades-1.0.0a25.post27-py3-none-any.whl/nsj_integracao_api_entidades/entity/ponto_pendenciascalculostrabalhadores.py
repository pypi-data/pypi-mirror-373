
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.pendenciascalculostrabalhadores",
    pk_field="pendenciacalculotrabalhador",
    default_order_fields=["pendenciacalculotrabalhador"],
)
class PendenciascalculostrabalhadoreEntity(EntityBase):
    pendenciacalculotrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    apuracaoponto: uuid.UUID = None
    origem: int = None
    datahora: datetime.datetime = None
    historico: bool = None
    lancamento: bool = None
    pagamento: bool = None
    lastupdate: datetime.datetime = None
    data: datetime.datetime = None
