
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.bancos",
    pk_field="banco",
    default_order_fields=["codigo"],
)
class BancoEntity(EntityBase):
    banco: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    numero: str = None
    tipoimpressao: int = None
    lastupdate: datetime.datetime = None
    codigoispb: str = None
