
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.pessoasparcelamentos",
    pk_field="pessoaparcelamento",
    default_order_fields=["pessoaparcelamento"],
)
class PessoasparcelamentoEntity(EntityBase):
    pessoaparcelamento: uuid.UUID = None
    tenant: int = None
    pessoa: uuid.UUID = None
    parcelamento: uuid.UUID = None
    lastupdate: datetime.datetime = None
