
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecoscategorias",
    pk_field="tabeladeprecocategoria",
    default_order_fields=["tabeladeprecocategoria"],
)
class TabelasdeprecoscategoriaEntity(EntityBase):
    tabeladeprecocategoria: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    id_categoriadeproduto: uuid.UUID = None
    lastupdate: datetime.datetime = None
