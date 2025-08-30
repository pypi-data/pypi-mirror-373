
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="scritta.tabicms",
    pk_field="id",
    default_order_fields=["uflocal"],
)
class TabicmEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    uflocal: str = None
    uf: str = None
    interno: float = None
    entrada: float = None
    saida: float = None
    redinterno: float = None
    redentrada: float = None
    redsaida: float = None
    lastupdate: datetime.datetime = None
