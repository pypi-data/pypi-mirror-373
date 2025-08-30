
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.promocoesleads",
    pk_field="promocaolead",
    default_order_fields=["codigo"],
)
class PromocoesleadEntity(EntityBase):
    promocaolead: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    inicio: datetime.datetime = None
    fim: datetime.datetime = None
    visivelfollowups: int = None
    visivelpropostas: int = None
    visivelleads: int = None
    visivelleadsqualificados: int = None
    envianotificacao: int = None
    templatenotificacao: str = None
    lastupdate: datetime.datetime = None
    id_grupoempresarial: uuid.UUID = None
    bloqueado: bool = None
    created_by: dict = None
    updated_by: dict = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
