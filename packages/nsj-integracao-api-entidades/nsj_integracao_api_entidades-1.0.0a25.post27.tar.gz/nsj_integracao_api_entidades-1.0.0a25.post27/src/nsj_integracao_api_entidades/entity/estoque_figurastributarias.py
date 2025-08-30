
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.figurastributarias",
    pk_field="figuratributaria",
    default_order_fields=["codigo"],
)
class FigurastributariaEntity(EntityBase):
    figuratributaria: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    perfilestadualpadrao: uuid.UUID = None
    perfilfederalpadrao: uuid.UUID = None
    id_grupo_empresarial: uuid.UUID = None
    id_empresa: uuid.UUID = None
