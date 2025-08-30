
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class AvisosferiastrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='avisoferiastrabalhador',
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
    data: datetime.datetime = DTOField(
      not_null=True,)
    datainiciogozo: datetime.datetime = DTOField()
    datafimgozo: datetime.datetime = DTOField()
    datainicioperiodoaquisitivo: datetime.datetime = DTOField()
    datafimperiodoaquisitivo: datetime.datetime = DTOField()
    temabonopecuniario: bool = DTOField()
    observacao: str = DTOField()
    tipo: int = DTOField(
      not_null=True,)
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    diasvendidos: int = DTOField()
    diasferiascoletivas: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    faltas: int = DTOField()
    adto13nasferias: bool = DTOField()
    consideraravisoparacalculovt: bool = DTOField()
    situacao: int = DTOField()
    origem: int = DTOField()
    created_at: datetime.datetime = DTOField(
      not_null=True,)
    consideraravisoparacalculoben: bool = DTOField()
    solicitacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

