
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.ra_movimentos",
    pk_field="ra_movimento",
    default_order_fields=["ra_movimento"],
)
class RaMovimentoEntity(EntityBase):
    ra_movimento: uuid.UUID = None
    tenant: int = None
    ra: uuid.UUID = None
    ra_item: uuid.UUID = None
    tipo: int = None
    quantidade_necessaria: float = None
    quantidade_apurada: float = None
    conferido: bool = None
    localdeestoque: uuid.UUID = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    grupoempresarial: uuid.UUID = None
