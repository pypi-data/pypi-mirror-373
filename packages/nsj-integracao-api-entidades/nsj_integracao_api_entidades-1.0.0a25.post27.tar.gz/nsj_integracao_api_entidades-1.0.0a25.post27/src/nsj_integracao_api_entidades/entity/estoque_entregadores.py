
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.entregadores",
    pk_field="entregador",
    default_order_fields=["entregador"],
)
class EntregadoreEntity(EntityBase):
    entregador: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    cnpj: str = None
    identidade: str = None
    id_empresa: uuid.UUID = None
    email: str = None
    bloqueado: bool = None
    telefone: str = None
    foto_filename: str = None
    id_motorista: uuid.UUID = None
    custo_hora: float = None
