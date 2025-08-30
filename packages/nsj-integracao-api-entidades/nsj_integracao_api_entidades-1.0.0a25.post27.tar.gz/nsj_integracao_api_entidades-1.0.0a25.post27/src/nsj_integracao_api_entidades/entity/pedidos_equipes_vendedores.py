
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.equipes_vendedores",
    pk_field="equipe_vendedor",
    default_order_fields=["equipe_vendedor"],
)
class EquipeVendedoreEntity(EntityBase):
    equipe_vendedor: uuid.UUID = None
    tenant: int = None
    id_equipe: uuid.UUID = None
    vendedor: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
