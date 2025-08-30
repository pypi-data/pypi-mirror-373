
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecosuf",
    pk_field="id",
    default_order_fields=["id"],
)
class TabelasdeprecosufEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    codigo_uf: str = None
    tipo: int = None
    lastupdate: datetime.datetime = None
