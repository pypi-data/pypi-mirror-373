
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.classificacoes",
    pk_field="classificacao",
    default_order_fields=["classificacao"],
)
class ClassificacoEntity(EntityBase):
    classificacao: uuid.UUID = None
    tenant: int = None
    valorinteiro: int = None
    valortexto: str = None
    classificador: uuid.UUID = None
    classificado: uuid.UUID = None
    valorclassificadorlista: uuid.UUID = None
    lastupdate: datetime.datetime = None
