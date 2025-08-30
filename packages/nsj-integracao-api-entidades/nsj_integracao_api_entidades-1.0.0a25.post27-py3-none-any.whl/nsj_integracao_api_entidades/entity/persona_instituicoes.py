
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.instituicoes",
    pk_field="instituicao",
    default_order_fields=["codigo"],
)
class InstituicoEntity(EntityBase):
    instituicao: uuid.UUID = None
    tenant: int = None
    tipo: int = None
    codigo: str = None
    nome: str = None
    cnpj: str = None
    registroans: str = None
    cnes: str = None
    ddd: str = None
    telefone: str = None
    lastupdate: datetime.datetime = None
