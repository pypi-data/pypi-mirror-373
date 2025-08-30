
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.associacoesitensnotas",
    pk_field="associacaoitemnota",
    default_order_fields=["associacaoitemnota"],
)
class AssociacoesitensnotaEntity(EntityBase):
    associacaoitemnota: uuid.UUID = None
    tenant: int = None
    id_docorigem: uuid.UUID = None
    id_docreferenciado: uuid.UUID = None
    id_linhadocreferenciado: uuid.UUID = None
    item: uuid.UUID = None
    id_linhadocorigem: uuid.UUID = None
    quantidade: float = None
    lastupdate: datetime.datetime = None
    ispce: bool = None
