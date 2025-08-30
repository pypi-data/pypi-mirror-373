
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.rotas",
    pk_field="rota",
    default_order_fields=["codigo"],
)
class RotaEntity(EntityBase):
    rota: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    grupoempresarial: uuid.UUID = None
    pesomaximo: float = None
    quantidademaxima: int = None
    valormaximo: float = None
    lastupdate: datetime.datetime = None
