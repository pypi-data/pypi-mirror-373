
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.tabelasdeprecosvendedores",
    pk_field="tabeladeprecovendedor",
    default_order_fields=["tabeladeprecovendedor"],
)
class TabelasdeprecosvendedoreEntity(EntityBase):
    tabeladeprecovendedor: uuid.UUID = None
    tenant: int = None
    tabeladepreco: uuid.UUID = None
    vendedor: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
