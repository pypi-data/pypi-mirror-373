
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.pessoas_produtos_consumidos",
    pk_field="pessoa_produto_consumido",
    default_order_fields=["pessoa_produto_consumido"],
)
class PessoaProdutoConsumidoEntity(EntityBase):
    pessoa_produto_consumido: uuid.UUID = None
    tenant: int = None
    pessoa: uuid.UUID = None
    categoria: uuid.UUID = None
    familia: uuid.UUID = None
    tipo: int = None
    created_by: dict = None
    created_at: datetime.datetime = None
    updated_by: dict = None
    updated_at: datetime.datetime = None
