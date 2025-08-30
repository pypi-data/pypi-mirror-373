
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.valestransportespersonalizadostrabalhadores",
    pk_field="valetransportepersonalizadotrabalhador",
    default_order_fields=["valetransportepersonalizadotrabalhador"],
)
class ValestransportespersonalizadostrabalhadoreEntity(EntityBase):
    valetransportepersonalizadotrabalhador: uuid.UUID = None
    tenant: int = None
    datainicial: datetime.datetime = None
    datafinal: datetime.datetime = None
    tipo: int = None
    conteudo: float = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    situacao: int = None
    origem: int = None
    motivo: int = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
    justificativa: str = None
    solicitacao: uuid.UUID = None
