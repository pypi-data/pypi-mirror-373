
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.papeisequipes",
    pk_field="papelequipe",
    default_order_fields=["papelequipe"],
)
class PapeisequipeEntity(EntityBase):
    papelequipe: uuid.UUID = None
    tenant: int = None
    papel: uuid.UUID = None
    equipe: uuid.UUID = None
    lastupdate: datetime.datetime = None
    escopoworkflow: int = None
