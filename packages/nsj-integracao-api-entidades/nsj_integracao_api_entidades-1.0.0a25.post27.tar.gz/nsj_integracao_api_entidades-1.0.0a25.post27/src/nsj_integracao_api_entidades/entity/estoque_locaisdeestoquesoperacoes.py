
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.locaisdeestoquesoperacoes",
    pk_field="localdeestoqueoperacao",
    default_order_fields=["localdeestoqueoperacao"],
)
class LocaisdeestoquesoperacoEntity(EntityBase):
    localdeestoqueoperacao: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    localdeestoque: uuid.UUID = None
    operacao: uuid.UUID = None
    lastupdate: datetime.datetime = None
