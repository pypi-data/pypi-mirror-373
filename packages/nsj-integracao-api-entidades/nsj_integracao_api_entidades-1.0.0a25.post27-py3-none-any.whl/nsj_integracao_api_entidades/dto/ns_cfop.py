
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class CfopDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='id',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    tipo: int = DTOField(
      not_null=True,)
    cfop: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    grupo: int = DTOField()
    descricao: str = DTOField()
    retorno: bool = DTOField()
    statusicms: int = DTOField()
    statusipi: int = DTOField()
    rapis: int = DTOField()
    remas: int = DTOField()
    tipomov: int = DTOField()
    soposse: bool = DTOField()
    transporte: bool = DTOField()
    cnae: str = DTOField()
    codserv: str = DTOField()
    cpsrb: str = DTOField()
    observacao: str = DTOField()
    discriminacaorps: str = DTOField()
    retempis: bool = DTOField()
    retemcofins: bool = DTOField()
    retemcsll: bool = DTOField()
    retemirrf: bool = DTOField()
    ibptaxa: float = DTOField()
    lastupdate: datetime.datetime = DTOField()
    aliquotaiss: float = DTOField()
    cfopservico: bool = DTOField()
    reducaobase: float = DTOField()
    ibptaxamunicipal: float = DTOField()
    ibptaxafederal: float = DTOField()
    incluirdeducoes: bool = DTOField()

