
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.cfop",
    pk_field="id",
    default_order_fields=["cfop"],
)
class CfopEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    tipo: int = None
    cfop: str = None
    grupo: int = None
    descricao: str = None
    retorno: bool = None
    statusicms: int = None
    statusipi: int = None
    rapis: int = None
    remas: int = None
    tipomov: int = None
    soposse: bool = None
    transporte: bool = None
    cnae: str = None
    codserv: str = None
    cpsrb: str = None
    observacao: str = None
    discriminacaorps: str = None
    retempis: bool = None
    retemcofins: bool = None
    retemcsll: bool = None
    retemirrf: bool = None
    ibptaxa: float = None
    lastupdate: datetime.datetime = None
    aliquotaiss: float = None
    cfopservico: bool = None
    reducaobase: float = None
    ibptaxamunicipal: float = None
    ibptaxafederal: float = None
    incluirdeducoes: bool = None
