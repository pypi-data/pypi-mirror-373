
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.ra",
    pk_field="ra",
    default_order_fields=["ra"],
)
class RaEntity(EntityBase):
    ra: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    responsavel: uuid.UUID = None
    data: datetime.datetime = None
    numero: int = None
    origem: int = None
    documento: uuid.UUID = None
    status: int = None
    lastupdate: datetime.datetime = None
    cliente: uuid.UUID = None
    observacao: str = None
    sinal: int = None
    localdeuso: uuid.UUID = None
    uso_consumo: bool = None
    id_operacao: uuid.UUID = None
    id_tecnico: uuid.UUID = None
    divergencia_local_estoque: bool = None
    divergencia_solucionada: bool = None
    contanasajon: str = None
