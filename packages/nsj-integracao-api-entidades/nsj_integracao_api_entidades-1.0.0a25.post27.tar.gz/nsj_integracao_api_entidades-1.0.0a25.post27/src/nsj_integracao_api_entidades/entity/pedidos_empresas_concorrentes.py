
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.empresas_concorrentes",
    pk_field="empresa_concorrente",
    default_order_fields=["codigo"],
)
class EmpresaConcorrenteEntity(EntityBase):
    empresa_concorrente: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
