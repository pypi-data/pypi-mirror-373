
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.tabelasdeprecosfamilias",
    pk_field="tabeladeprecofamilia",
    default_order_fields=["tabeladeprecofamilia"],
)
class TabelasdeprecosfamiliaEntity(EntityBase):
    tabeladeprecofamilia: uuid.UUID = None
    tenant: int = None
    id_tabeladepreco: uuid.UUID = None
    id_familia: uuid.UUID = None
    lastupdate: datetime.datetime = None
