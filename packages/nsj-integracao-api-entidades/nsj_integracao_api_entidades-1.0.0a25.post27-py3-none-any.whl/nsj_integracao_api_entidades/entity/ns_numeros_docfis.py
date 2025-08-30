
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.numeros_docfis",
    pk_field="id",
    default_order_fields=["id"],
)
class NumeroDocfiEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    id_estabelecimento: uuid.UUID = None
    id_operacao: uuid.UUID = None
    proximo_numero: int = None
    lastupdate: datetime.datetime = None
