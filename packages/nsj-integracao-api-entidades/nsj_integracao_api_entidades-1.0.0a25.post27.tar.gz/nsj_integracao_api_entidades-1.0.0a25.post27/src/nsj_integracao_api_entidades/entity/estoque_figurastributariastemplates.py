
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.figurastributariastemplates",
    pk_field="figuratributariatemplate",
    default_order_fields=["figuratributariatemplate"],
)
class FigurastributariastemplateEntity(EntityBase):
    figuratributariatemplate: uuid.UUID = None
    tenant: int = None
    figuratributaria: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    operacao: uuid.UUID = None
    perfiltributario_estadual: uuid.UUID = None
    perfiltributario_federal: uuid.UUID = None
    lastupdate: datetime.datetime = None
    perfil_federal_simples: uuid.UUID = None
