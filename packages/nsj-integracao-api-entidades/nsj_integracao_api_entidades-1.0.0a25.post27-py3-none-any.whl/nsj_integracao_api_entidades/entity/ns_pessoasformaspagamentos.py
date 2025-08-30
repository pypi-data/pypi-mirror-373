
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.pessoasformaspagamentos",
    pk_field="pessoaformapagamento",
    default_order_fields=["pessoaformapagamento"],
)
class PessoasformaspagamentoEntity(EntityBase):
    pessoaformapagamento: uuid.UUID = None
    tenant: int = None
    pessoa: uuid.UUID = None
    formapagamento: uuid.UUID = None
    lastupdate: datetime.datetime = None
