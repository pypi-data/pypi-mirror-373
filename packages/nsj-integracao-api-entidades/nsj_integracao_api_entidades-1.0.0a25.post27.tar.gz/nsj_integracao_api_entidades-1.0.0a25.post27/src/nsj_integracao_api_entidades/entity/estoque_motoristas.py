
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.motoristas",
    pk_field="motorista",
    default_order_fields=["codigo"],
)
class MotoristaEntity(EntityBase):
    motorista: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    cpf: str = None
    nome: str = None
    cnh: str = None
    datavenctocnh: datetime.datetime = None
    empresa: uuid.UUID = None
    lastupdate: datetime.datetime = None
