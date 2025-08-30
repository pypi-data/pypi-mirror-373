
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.acoes",
    pk_field="acao",
    default_order_fields=["acao"],
)
class AcoEntity(EntityBase):
    acao: uuid.UUID = None
    tenant: int = None
    estadoorigem: uuid.UUID = None
    estadodestino: uuid.UUID = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    fixo: bool = None
    multiplasexecucoes: bool = None
    logicamultiplasexecucoes: int = None
    verificaalcada: bool = None
    ordem: int = None
    buttonindeximage: int = None
    lastupdate: datetime.datetime = None
    escopoworkflow: int = None
