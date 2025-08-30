
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.faltastrabalhadores",
    pk_field="faltatrabalhador",
    default_order_fields=["faltatrabalhador"],
)
class FaltastrabalhadoreEntity(EntityBase):
    faltatrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    descricao: str = None
    tipo: int = None
    trabalhador: uuid.UUID = None
    descontaponto: bool = None
    status: int = None
    lastupdate: datetime.datetime = None
    responsavel: uuid.UUID = None
    solicitante: uuid.UUID = None
    datacriacao: datetime.datetime = None
    datamudancaestado: datetime.datetime = None
    emailresponsavel: str = None
    observacao: str = None
    compensacao: bool = None
    origem: int = None
    mesdescontocalculo: int = None
    anodescontocalculo: int = None
    estabelecimento: uuid.UUID = None
    solicitacao: uuid.UUID = None
    descontavr: bool = None
    descontavt: bool = None
    descontava: bool = None
