
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.equipes",
    pk_field="equipe",
    default_order_fields=["equipe"],
)
class EquipeEntity(EntityBase):
    equipe: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    escopoworkflow: int = None
