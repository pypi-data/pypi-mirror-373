
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.contatos",
    pk_field="id",
    default_order_fields=["id"],
)
class ContatoEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    nome: str = None
    nascimento: datetime.datetime = None
    cargo: str = None
    sexomasculino: bool = None
    observacao: str = None
    email: str = None
    primeironome: str = None
    sobrenome: str = None
    id_pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
    principal: bool = None
    cpf: str = None
    responsavellegal: bool = None
    decisor: bool = None
    influenciador: bool = None
