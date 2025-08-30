
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.valoresclassificadoreslista",
    pk_field="valorclassificadorlista",
    default_order_fields=["valorclassificadorlista"],
)
class ValoresclassificadoreslistaEntity(EntityBase):
    valorclassificadorlista: uuid.UUID = None
    tenant: int = None
    etiqueta: str = None
    classificador: uuid.UUID = None
    lastupdate: datetime.datetime = None
