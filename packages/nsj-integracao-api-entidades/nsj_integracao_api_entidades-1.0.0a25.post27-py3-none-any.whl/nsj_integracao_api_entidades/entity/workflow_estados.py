
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.estados",
    pk_field="estado",
    default_order_fields=["estado"],
)
class EstadoEntity(EntityBase):
    estado: uuid.UUID = None
    tenant: int = None
    diagrama: uuid.UUID = None
    papel: uuid.UUID = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    tipo: int = None
    bloqueiadelegacao: bool = None
    ordem: int = None
    lastupdate: datetime.datetime = None
    imageindex: int = None
    prazopadrao: int = None
    escopoworkflow: int = None
    tipo_permissao: int = None
    gerar_pendencia: bool = None
