
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.beneficiostrabalhadores",
    pk_field="beneficiotrabalhador",
    default_order_fields=["beneficiotrabalhador"],
)
class BeneficiostrabalhadoreEntity(EntityBase):
    beneficiotrabalhador: uuid.UUID = None
    tenant: int = None
    valor: float = None
    valordesconto: float = None
    quantidade: int = None
    tipoperiodo: int = None
    mesperiodo: int = None
    mesinicialperiodo: int = None
    mesfinalperiodo: int = None
    anoinicialperiodo: int = None
    anofinalperiodo: int = None
    beneficio: uuid.UUID = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    lotacao: uuid.UUID = None
    dataadesao: datetime.datetime = None
    dataexclusao: datetime.datetime = None
    dependentetrabalhador: uuid.UUID = None
