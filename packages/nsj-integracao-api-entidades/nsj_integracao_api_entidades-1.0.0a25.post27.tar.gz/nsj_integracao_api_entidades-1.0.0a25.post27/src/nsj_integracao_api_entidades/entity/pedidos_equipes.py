
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.equipes",
    pk_field="equipe",
    default_order_fields=["nome"],
)
class EquipeEntity(EntityBase):
    equipe: uuid.UUID = None
    tenant: int = None
    nome: str = None
    responsavel: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
