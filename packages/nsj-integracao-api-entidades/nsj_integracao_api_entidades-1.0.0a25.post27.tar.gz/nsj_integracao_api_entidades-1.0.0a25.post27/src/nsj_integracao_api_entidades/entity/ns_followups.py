
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.followups",
    pk_field="followup",
    default_order_fields=["followup"],
)
class FollowupEntity(EntityBase):
    followup: uuid.UUID = None
    tenant: int = None
    historico: str = None
    data: datetime.datetime = None
    tempoatendimento: int = None
    oportunidade: uuid.UUID = None
    promocaolead: uuid.UUID = None
    departamento: uuid.UUID = None
    participante: uuid.UUID = None
    tipofollowup: uuid.UUID = None
    usuario: uuid.UUID = None
    atendimento: uuid.UUID = None
    ordemservico: uuid.UUID = None
    lastupdate: datetime.datetime = None
    proposta: uuid.UUID = None
    atendimentonegociacao: uuid.UUID = None
    pedidogerencial: uuid.UUID = None
    responsavel: str = None
    tipo: int = None
    resumo: str = None
    criadopelocliente: bool = None
    created_by: dict = None
    canal: str = None
    canal_email: str = None
    artigo: uuid.UUID = None
    mesclado_a: uuid.UUID = None
    romaneio_entrega: uuid.UUID = None
    romaneio: uuid.UUID = None
    ativo: bool = None
    receptor: str = None
    meiocomunicacao: int = None
    figuracontato: int = None
    automatico: bool = None
    lido: bool = None
    copiaoculta: str = None
