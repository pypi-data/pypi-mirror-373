
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.solicitacoesprodutosservicos",
    pk_field="solicitacaoprodutoservico",
    default_order_fields=["solicitante"],
)
class SolicitacoesprodutosservicoEntity(EntityBase):
    solicitacaoprodutoservico: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    solicitante: str = None
    numero: str = None
    datalimite: datetime.datetime = None
    motivo: str = None
    rateio: uuid.UUID = None
    data_cadastro: datetime.datetime = None
    cadastrado_por: str = None
    situacao: int = None
    localdeuso_padrao: uuid.UUID = None
    wkf_data: datetime.datetime = None
    wkf_estado: str = None
    uso_consumo: bool = None
    cliente: uuid.UUID = None
    localdeuso_modelo: uuid.UUID = None
    origem: int = None
    id_documento_origem: uuid.UUID = None
    rascunho: bool = None
    lastupdate: datetime.datetime = None
