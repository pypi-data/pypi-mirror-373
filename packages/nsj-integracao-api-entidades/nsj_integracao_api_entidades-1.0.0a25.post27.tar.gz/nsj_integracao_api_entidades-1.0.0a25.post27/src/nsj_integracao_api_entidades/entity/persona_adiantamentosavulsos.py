
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.adiantamentosavulsos",
    pk_field="adiantamentoavulso",
    default_order_fields=["adiantamentoavulso"],
)
class AdiantamentosavulsoEntity(EntityBase):
    adiantamentoavulso: uuid.UUID = None
    tenant: int = None
    eventorendimento: uuid.UUID = None
    eventodesconto: uuid.UUID = None
    trabalhador: uuid.UUID = None
    historicoadiantamentoavulso: uuid.UUID = None
    datacadastro: datetime.datetime = None
    valor: float = None
    observacao: str = None
    formapagamento: int = None
    mescompetencia: int = None
    anocompetencia: int = None
    situacao: int = None
    lastupdate: datetime.datetime = None
    datapagamento: datetime.datetime = None
    created_at: datetime.datetime = None
    origem: int = None
    created_by: dict = None
    updated_by: dict = None
    numero: int = None
    justificativa: str = None
    solicitacao: uuid.UUID = None
