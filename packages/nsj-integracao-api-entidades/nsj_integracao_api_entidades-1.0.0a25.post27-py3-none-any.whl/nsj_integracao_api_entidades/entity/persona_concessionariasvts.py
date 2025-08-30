
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.concessionariasvts",
    pk_field="concessionariavt",
    default_order_fields=["codigo"],
)
class ConcessionariasvtEntity(EntityBase):
    concessionariavt: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    lastupdate: datetime.datetime = None
