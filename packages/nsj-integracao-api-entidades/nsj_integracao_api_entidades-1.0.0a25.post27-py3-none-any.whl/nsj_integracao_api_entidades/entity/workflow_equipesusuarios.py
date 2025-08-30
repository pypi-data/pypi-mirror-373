
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.equipesusuarios",
    pk_field="equipeusuario",
    default_order_fields=["equipeusuario"],
)
class EquipesusuarioEntity(EntityBase):
    equipeusuario: uuid.UUID = None
    tenant: int = None
    equipe: uuid.UUID = None
    usuario: uuid.UUID = None
    lastupdate: datetime.datetime = None
    escopoworkflow: int = None
