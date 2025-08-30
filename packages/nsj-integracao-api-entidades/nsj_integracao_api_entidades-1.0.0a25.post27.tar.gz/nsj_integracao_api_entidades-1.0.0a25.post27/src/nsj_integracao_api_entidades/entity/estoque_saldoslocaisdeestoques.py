
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.saldoslocaisdeestoques",
    pk_field="saldolocaldeestoque",
    default_order_fields=["saldolocaldeestoque"],
)
class SaldoslocaisdeestoqueEntity(EntityBase):
    saldolocaldeestoque: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    localdeestoque: uuid.UUID = None
    item: uuid.UUID = None
    slot: str = None
    data: datetime.datetime = None
    entradas: float = None
    saidas: float = None
    saldo: float = None
    inventario: uuid.UUID = None
    custototal: float = None
    pmc: float = None
    lastupdate: datetime.datetime = None
    produto: uuid.UUID = None
