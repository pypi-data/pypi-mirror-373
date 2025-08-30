
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.telefones",
    pk_field="id",
    default_order_fields=["id"],
)
class TelefoneEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    ddd: str = None
    telefone: str = None
    chavetel: str = None
    descricao: str = None
    ramal: str = None
    tptelefone: int = None
    ddi: str = None
    ordemimportancia: int = None
    contato: uuid.UUID = None
    id_pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
    principal: bool = None
