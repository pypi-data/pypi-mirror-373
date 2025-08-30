
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.agencias",
    pk_field="agencia",
    default_order_fields=["codigo"],
)
class AgenciaEntity(EntityBase):
    agencia: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    agencianumero: str = None
    digitoverificador: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    bairro: str = None
    cidade: str = None
    estado: str = None
    cep: str = None
    contato: str = None
    telefone: str = None
    dddtel: str = None
    banco: uuid.UUID = None
    lastupdate: datetime.datetime = None
