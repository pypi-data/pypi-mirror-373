
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tarifasconcessionariasvtstrabalhadores",
    pk_field="tarifaconcessionariavttrabalhador",
    default_order_fields=["tarifaconcessionariavttrabalhador"],
)
class TarifasconcessionariasvtstrabalhadoreEntity(EntityBase):
    tarifaconcessionariavttrabalhador: uuid.UUID = None
    tenant: int = None
    quantidade: int = None
    trabalhador: uuid.UUID = None
    tarifaconcessionariavt: uuid.UUID = None
    lastupdate: datetime.datetime = None
