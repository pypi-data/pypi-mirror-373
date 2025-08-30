
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.produtosvendedores",
    pk_field="produtovendedor",
    default_order_fields=["produtovendedor"],
)
class ProdutosvendedoreEntity(EntityBase):
    produtovendedor: uuid.UUID = None
    tenant: int = None
    produto: uuid.UUID = None
    vendedor: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
