
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.contasfornecedores",
    pk_field="contafornecedor",
    default_order_fields=["contafornecedor"],
)
class ContasfornecedoreEntity(EntityBase):
    contafornecedor: uuid.UUID = None
    tenant: int = None
    banco: str = None
    agencianumero: str = None
    agenciadv: str = None
    agencianome: str = None
    contanumero: str = None
    contadv: str = None
    tipoconta: int = None
    id_fornecedor: uuid.UUID = None
    padrao: bool = None
    excluida: bool = None
    lastupdate: datetime.datetime = None
