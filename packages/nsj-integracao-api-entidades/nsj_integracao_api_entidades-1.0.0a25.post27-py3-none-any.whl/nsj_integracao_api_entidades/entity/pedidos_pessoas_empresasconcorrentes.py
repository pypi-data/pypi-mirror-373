
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.pessoas_empresasconcorrentes",
    pk_field="pessoa_empresaconcorrente",
    default_order_fields=["pessoa_empresaconcorrente"],
)
class PessoaEmpresasconcorrenteEntity(EntityBase):
    pessoa_empresaconcorrente: uuid.UUID = None
    tenant: int = None
    pessoa: uuid.UUID = None
    empresa_concorrente: uuid.UUID = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
