
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.potenciais_portfolios",
    pk_field="potencial_portfolio",
    default_order_fields=["codigo"],
)
class PotenciaiPortfolioEntity(EntityBase):
    potencial_portfolio: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    peso: float = None
    created_by: dict = None
    created_at: datetime.datetime = None
    updated_by: dict = None
    updated_at: datetime.datetime = None
