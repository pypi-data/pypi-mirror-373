
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.obras",
    pk_field="id",
    default_order_fields=["id"],
)
class ObraEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    obra: int = None
    codigonfse: str = None
    descricao: str = None
    inicio: datetime.datetime = None
    cei: str = None
    fim: datetime.datetime = None
    habite_se: datetime.datetime = None
    inativa: bool = None
    tipologradouro: str = None
    endereco: str = None
    numero: str = None
    complemento: str = None
    bairro: str = None
    municipio: str = None
    cidade: str = None
    estado: str = None
    cep: str = None
    art: str = None
    tpobra: int = None
    unidades: int = None
    upcs: int = None
    area: float = None
    aliquotarat: float = None
    aliquotafap: float = None
    cnae: str = None
    aliquotaterceiros: float = None
    cpf: str = None
    raizcnpj: str = None
    ordemcnpj: str = None
    tipoidentificacao: int = None
    contribuicaopatronalsubstituida: bool = None
    cno: str = None
    id_estabelecimento: uuid.UUID = None
    id_orgao: uuid.UUID = None
    id_pessoa: uuid.UUID = None
    id_agente: uuid.UUID = None
    lastupdate: datetime.datetime = None
