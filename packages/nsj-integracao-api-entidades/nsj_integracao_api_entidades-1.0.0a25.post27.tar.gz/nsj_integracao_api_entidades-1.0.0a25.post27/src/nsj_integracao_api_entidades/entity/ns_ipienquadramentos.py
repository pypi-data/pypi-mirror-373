
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.ipienquadramentos",
    pk_field="ipienquadramento",
    default_order_fields=["codigo"],
)
class IpienquadramentoEntity(EntityBase):
    ipienquadramento: uuid.UUID = None
    tenant: int = None
    grupocst: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
