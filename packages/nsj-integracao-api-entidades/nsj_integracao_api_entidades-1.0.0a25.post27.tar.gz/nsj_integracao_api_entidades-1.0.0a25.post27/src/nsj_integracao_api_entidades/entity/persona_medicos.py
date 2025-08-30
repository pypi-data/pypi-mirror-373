
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.medicos",
    pk_field="medico",
    default_order_fields=["codigo"],
)
class MedicoEntity(EntityBase):
    medico: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nit: str = None
    numeroregistroconselho: str = None
    nome: str = None
    categoria: int = None
    ufcrm: str = None
    dddtelefone: str = None
    telefone: str = None
    tipocrm: str = None
    tipoconselho: int = None
    lastupdate: datetime.datetime = None
