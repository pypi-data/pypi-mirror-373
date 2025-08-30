
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.processos",
    pk_field="processo",
    default_order_fields=["processo"],
)
class ProcessoEntity(EntityBase):
    processo: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    esquema: str = None
    tabela: str = None
    campoid: str = None
    campovalor: str = None
    sistema: int = None
    lastupdate: datetime.datetime = None
    ativo: bool = None
    escopoworkflow: int = None
