
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.negociacoes",
    pk_field="negociacao",
    default_order_fields=["negociacao"],
)
class NegociacoEntity(EntityBase):
    negociacao: uuid.UUID = None
    tenant: int = None
    usuarioresponsavel: uuid.UUID = None
    requisicaocompra: uuid.UUID = None
    valorprodutosservicos: float = None
    valorfrete: float = None
    valoroutrasdespesas: float = None
    valortotal: float = None
    status: int = None
    datahoraabertura: datetime.datetime = None
    datahoraprocessamento: datetime.datetime = None
    estabelecimento: uuid.UUID = None
    numero: int = None
    lastupdate: datetime.datetime = None
    valortributos: float = None
    wkf_estado: str = None
    wkf_data: datetime.datetime = None
    localdeuso: uuid.UUID = None
