
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.pagamentoslancamentos",
    pk_field="pagamentolancamento",
    default_order_fields=["pagamentolancamento"],
)
class PagamentoslancamentoEntity(EntityBase):
    pagamentolancamento: uuid.UUID = None
    tenant: int = None
    lancamento: uuid.UUID = None
    mes: int = None
    ano: int = None
    valor: int = None
    lastupdate: datetime.datetime = None
