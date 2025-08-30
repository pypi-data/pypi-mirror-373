
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_parcelas",
    pk_field="parcela",
    default_order_fields=["parcela"],
)
class DfParcelaEntity(EntityBase):
    parcela: uuid.UUID = None
    tenant: int = None
    id_pagamento: uuid.UUID = None
    numero: str = None
    valor: float = None
    vencimento: datetime.datetime = None
    sequencial: int = None
    lastupdate: datetime.datetime = None
    conta: uuid.UUID = None
    usarsaldocredito: bool = None
    valorcreditoautilizar: float = None
    competencia: datetime.datetime = None
    basevencimentoparcela: uuid.UUID = None
    percentual: float = None
    intervalo: int = None
    sinal: bool = None
    valoresalteradosmanualmente: bool = None
