
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.ra_itens",
    pk_field="ra_item",
    default_order_fields=["ra_item"],
)
class RaItenEntity(EntityBase):
    ra_item: uuid.UUID = None
    tenant: int = None
    ra: uuid.UUID = None
    item: uuid.UUID = None
    quantidade_requisitada: float = None
    status: int = None
    lastupdate: datetime.datetime = None
    localdeestoque: uuid.UUID = None
    valorunitario: float = None
    quantidade_diferenca: float = None
    tipo_diferenca: int = None
    id_linhadocorigem: uuid.UUID = None
    itemcustomcodigo: str = None
    itemcustomdescricao: str = None
    valor_base: float = None
    desconto: float = None
    unidade: uuid.UUID = None
    localdeestoque_sugerido: uuid.UUID = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
