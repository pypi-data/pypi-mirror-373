
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.layoutscobrancas",
    pk_field="layoutcobranca",
    default_order_fields=["nome"],
)
class LayoutscobrancaEntity(EntityBase):
    layoutcobranca: uuid.UUID = None
    tenant: int = None
    implementacao: int = None
    nome: str = None
    layoutrelatorio: int = None
    banco: uuid.UUID = None
    lastupdate: datetime.datetime = None
