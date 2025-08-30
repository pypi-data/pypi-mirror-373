
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecosentidades",
    pk_field="tabeladeprecoentidade",
    default_order_fields=["tabeladeprecoentidade"],
)
class TabelasdeprecosentidadeEntity(EntityBase):
    tabeladeprecoentidade: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    id_pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
