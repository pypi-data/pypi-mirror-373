
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.tipos_objecoes",
    pk_field="tipo_objecao",
    default_order_fields=["tipo_objecao"],
)
class TipoObjecoEntity(EntityBase):
    tipo_objecao: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipo: int = None
