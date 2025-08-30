
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.pessoasmunicipios",
    pk_field="pessoamunicipio",
    default_order_fields=["ibge"],
)
class PessoasmunicipioEntity(EntityBase):
    pessoamunicipio: uuid.UUID = None
    tenant: int = None
    ibge: str = None
    pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
    grupoempresarial: uuid.UUID = None
