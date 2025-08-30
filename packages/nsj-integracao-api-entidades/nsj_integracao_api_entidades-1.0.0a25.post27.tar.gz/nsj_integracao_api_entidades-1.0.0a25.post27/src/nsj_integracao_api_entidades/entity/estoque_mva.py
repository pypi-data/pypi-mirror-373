
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.mva",
    pk_field="mva",
    default_order_fields=["mva"],
)
class MvaEntity(EntityBase):
    mva: uuid.UUID = None
    tenant: int = None
    uf: str = None
    ncm: uuid.UUID = None
    lastupdate: datetime.datetime = None
    inicio: datetime.datetime = None
    fim: datetime.datetime = None
    porcentagem_original: float = None
