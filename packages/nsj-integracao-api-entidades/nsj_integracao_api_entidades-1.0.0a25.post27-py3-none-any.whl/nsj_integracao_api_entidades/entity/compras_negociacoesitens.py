
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.negociacoesitens",
    pk_field="negociacaoitem",
    default_order_fields=["descricao"],
)
class NegociacoesitenEntity(EntityBase):
    negociacaoitem: uuid.UUID = None
    tenant: int = None
    negociacao: uuid.UUID = None
    id_item: uuid.UUID = None
    tipo_item: int = None
    ordem: int = None
    quantidadesolicitada: float = None
    descricao: str = None
    id_produto: uuid.UUID = None
    lastupdate: datetime.datetime = None
    codigo: str = None
    unidade: uuid.UUID = None
