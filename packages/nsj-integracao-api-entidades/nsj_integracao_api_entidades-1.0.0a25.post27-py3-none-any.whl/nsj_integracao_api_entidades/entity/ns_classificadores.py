
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.classificadores",
    pk_field="classificador",
    default_order_fields=["etiqueta"],
)
class ClassificadoreEntity(EntityBase):
    classificador: uuid.UUID = None
    tenant: int = None
    etiqueta: str = None
    modulo: int = None
    ordem: int = None
    tipo: int = None
    tamanhomaximo: int = None
    subclassificacao: int = None
    lastupdate: datetime.datetime = None
