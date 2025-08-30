
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.contaspadroes",
    pk_field="id",
    default_order_fields=["id"],
)
class ContaspadroEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    id_estabelecimento: uuid.UUID = None
    id_conta: uuid.UUID = None
    id_contamanutencao: uuid.UUID = None
    lastupdate: datetime.datetime = None
