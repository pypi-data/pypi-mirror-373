
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.perfiltrib_est",
    pk_field="perfiltrib_est",
    default_order_fields=["codigo"],
)
class PerfiltribEstEntity(EntityBase):
    perfiltrib_est: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    uf_origem: str = None
    icms_aliquotainterna: float = None
    lastupdate: datetime.datetime = None
    id_grupo_empresarial: uuid.UUID = None
    id_empresa: uuid.UUID = None
    situacao: int = None
    motivo: str = None
