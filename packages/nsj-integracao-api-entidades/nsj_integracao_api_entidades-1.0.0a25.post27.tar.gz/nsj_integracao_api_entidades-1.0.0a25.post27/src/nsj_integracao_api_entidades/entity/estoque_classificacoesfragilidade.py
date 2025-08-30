
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.classificacoesfragilidade",
    pk_field="classificacaofragilidade",
    default_order_fields=["codigo"],
)
class ClassificacoesfragilidadeEntity(EntityBase):
    classificacaofragilidade: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
