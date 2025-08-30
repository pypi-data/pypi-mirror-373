
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tiposanexos",
    pk_field="tipoanexo",
    default_order_fields=["tipoanexo"],
)
class TiposanexoEntity(EntityBase):
    tipoanexo: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    tipovalidacaoadimissao: int = None
    tipovalidacaoautocadastro: int = None
    lastupdate: datetime.datetime = None
