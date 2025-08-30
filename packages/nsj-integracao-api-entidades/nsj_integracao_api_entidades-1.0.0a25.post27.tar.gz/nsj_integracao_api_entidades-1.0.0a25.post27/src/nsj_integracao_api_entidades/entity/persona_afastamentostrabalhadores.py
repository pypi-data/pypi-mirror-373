
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.afastamentostrabalhadores",
    pk_field="afastamentotrabalhador",
    default_order_fields=["afastamentotrabalhador"],
)
class AfastamentostrabalhadoreEntity(EntityBase):
    afastamentotrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    dias: int = None
    tipohistorico: str = None
    descricao: str = None
    observacao: str = None
    cid: str = None
    cnpjempresacessionaria: str = None
    tipoonuscessionaria: int = None
    tipoonussindicato: int = None
    tipoacidentetransito: int = None
    datainicioperiodoaquisitivo: datetime.datetime = None
    diassaldoferias: int = None
    afastamentotrabalhadorpai: uuid.UUID = None
    trabalhador: uuid.UUID = None
    medico: uuid.UUID = None
    sindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
    estado: int = None
    dataproximasferias: datetime.datetime = None
    origem: int = None
    peloinss: bool = None
    semdataretorno: bool = None
    solicitacao: uuid.UUID = None
