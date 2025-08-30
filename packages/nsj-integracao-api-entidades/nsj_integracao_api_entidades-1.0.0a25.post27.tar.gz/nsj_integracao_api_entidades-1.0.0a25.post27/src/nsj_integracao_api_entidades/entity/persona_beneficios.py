
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.beneficios",
    pk_field="beneficio",
    default_order_fields=["codigo"],
)
class BeneficioEntity(EntityBase):
    beneficio: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipovalor: int = None
    tipobasevalor: int = None
    valor: float = None
    proporcionalizavalor: bool = None
    tipodesconto: int = None
    tipobasedesconto: int = None
    tipoaplicacaodesconto: int = None
    valordesconto: float = None
    tipoformulavalor: int = None
    tipoformuladesconto: int = None
    formulabasicacondicaovalor: str = None
    formulabasicacondicaodesconto: str = None
    formulabasicavalor: str = None
    formulabasicadesconto: str = None
    formulaavancadavalor: str = None
    formulaavancadadesconto: str = None
    empresa: uuid.UUID = None
    eventodesconto: uuid.UUID = None
    faixavalor: uuid.UUID = None
    faixadesconto: uuid.UUID = None
    tipobeneficio: uuid.UUID = None
    lastupdate: datetime.datetime = None
    permitedependente: bool = None
    tipobeneficiointerno: int = None
