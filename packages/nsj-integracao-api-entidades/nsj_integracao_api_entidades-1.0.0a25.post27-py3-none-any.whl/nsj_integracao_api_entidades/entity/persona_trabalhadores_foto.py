
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.trabalhadores",
    pk_field="trabalhador",
    default_order_fields=["trabalhador"],
)
class TrabalhadorFotoEntity(EntityBase):
    trabalhador: uuid.UUID = None
    tenant: int = None
    foto: bytes = None
    fotooriginal: bytes = None