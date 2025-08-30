
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.sindicatos",
    pk_field="sindicato",
    default_order_fields=["codigo"],
)
class SindicatoEntity(EntityBase):
    sindicato: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    bairro: str = None
    cidade: str = None
    cep: str = None
    codigocontribuicao: str = None
    cnpj: str = None
    codigoentidadesindical: str = None
    pisosalarial: float = None
    calculoeacumulativo: bool = None
    estado: str = None
    calculanofim: bool = None
    patronal: bool = None
    contato: str = None
    telefone: str = None
    dddtel: str = None
    fax: str = None
    dddfax: str = None
    email: str = None
    somentemaioranuenio: bool = None
    multafgts: float = None
    mesesmediamaternidade: int = None
    diadissidio: int = None
    diasaviso: int = None
    qtdemrre: int = None
    qtdemrfe: int = None
    qtdemr13: int = None
    mesassistencial: int = None
    mediaferiaspelomaiorvalor: bool = None
    media13pelomaiorvalor: bool = None
    mediarescisaopelomaiorvalor: bool = None
    mesdesconto: int = None
    mesdissidio: int = None
    mesesmediaferias: int = None
    mesesmediarescisao: int = None
    mesesmedia13: int = None
    numeradorfracao: int = None
    denominadorfracao: int = None
    fpas: str = None
    codigoterceiros: str = None
    lastupdate: datetime.datetime = None
    regraponto: uuid.UUID = None
