
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecosestabelecimentos",
    pk_field="tabeladeprecoestabelecimento",
    default_order_fields=["tabeladeprecoestabelecimento"],
)
class TabelasdeprecosestabelecimentoEntity(EntityBase):
    tabeladeprecoestabelecimento: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    id_estabelecimento: uuid.UUID = None
    lastupdate: datetime.datetime = None
