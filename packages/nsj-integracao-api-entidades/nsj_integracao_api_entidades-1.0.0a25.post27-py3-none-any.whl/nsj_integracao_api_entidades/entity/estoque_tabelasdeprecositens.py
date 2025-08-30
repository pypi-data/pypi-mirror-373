
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecositens",
    pk_field="tabeladeprecoitem",
    default_order_fields=["tabeladeprecoitem"],
)
class TabelasdeprecositenEntity(EntityBase):
    tabeladeprecoitem: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    id_item: uuid.UUID = None
    preco: float = None
    lastupdate: datetime.datetime = None
    descontomaximo: float = None
