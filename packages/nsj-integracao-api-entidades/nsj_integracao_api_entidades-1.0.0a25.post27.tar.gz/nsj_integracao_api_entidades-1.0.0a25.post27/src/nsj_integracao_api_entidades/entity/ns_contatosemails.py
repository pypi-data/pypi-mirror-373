
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.contatosemails",
    pk_field="id",
    default_order_fields=["id"],
)
class ContatosemailEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    pessoa_id: uuid.UUID = None
    contato_id: uuid.UUID = None
    email: str = None
    recebe_nfse: bool = None
    envia_nfse_prefeitura: bool = None
    recebe_nfe: bool = None
    envia_nfe_receita: bool = None
    recebe_boleto: bool = None
    recebe_pedido: bool = None
    recebe_cotacao_compra: bool = None
    lastupdate: datetime.datetime = None
    recebe_mala_direta: bool = None
    recebe_fatura_locacao: bool = None
    principal: bool = None
