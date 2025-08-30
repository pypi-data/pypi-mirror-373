
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.lotacoes",
    pk_field="lotacao",
    default_order_fields=["codigo"],
)
class LotacoEntity(EntityBase):
    lotacao: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    tipo: int = None
    enderecodiferente: bool = None
    tipologradouro: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    bairro: str = None
    cidade: str = None
    cep: str = None
    uf: str = None
    municipio: str = None
    centrocustonasajon: int = None
    classefinnasajon: int = None
    ccustopersona: str = None
    classefinpersona: str = None
    outrasentidadesdiferente: bool = None
    fpas: str = None
    codigoterceiros: str = None
    aliquotaterceiros: float = None
    agentenocivo: str = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    tomador: uuid.UUID = None
    obra: uuid.UUID = None
    processo: uuid.UUID = None
    lastupdate: datetime.datetime = None
    nuncaexpostoagentenocivo: bool = None
    regraponto: uuid.UUID = None
    bancohoras: bool = None
    desabilitado: bool = None
