
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.rotas_pessoas",
    pk_field="rota_pessoa",
    default_order_fields=["rota_pessoa"],
)
class RotaPessoaEntity(EntityBase):
    rota_pessoa: uuid.UUID = None
    tenant: int = None
    rota: uuid.UUID = None
    pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
