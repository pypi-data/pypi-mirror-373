
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_vendedores",
    pk_field="df_vendedor",
    default_order_fields=["df_vendedor"],
)
class DfVendedoreEntity(EntityBase):
    df_vendedor: uuid.UUID = None
    tenant: int = None
    id_docfis: uuid.UUID = None
    vendedor: uuid.UUID = None
    percentual: float = None
    padrao: bool = None
    lastupdate: datetime.datetime = None
    percentual_comissao: float = None
