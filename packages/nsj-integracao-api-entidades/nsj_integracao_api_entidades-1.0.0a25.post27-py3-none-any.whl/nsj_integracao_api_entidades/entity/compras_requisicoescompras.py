
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.requisicoescompras",
    pk_field="requisicaocompra",
    default_order_fields=["codigo"],
)
class RequisicoescompraEntity(EntityBase):
    requisicaocompra: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    solicitante: uuid.UUID = None
    codigo: str = None
    datalimite: datetime.datetime = None
    datacadastro: datetime.datetime = None
    justificativa: str = None
    lastupdate: datetime.datetime = None
    wkf_estado: str = None
    wkf_data: datetime.datetime = None
    categoriaprincipal: uuid.UUID = None
    localestoque: uuid.UUID = None
    analistacompra: uuid.UUID = None
    operacao: uuid.UUID = None
