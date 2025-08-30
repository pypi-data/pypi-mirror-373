
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.persona_processosrubricas import ProcessosrubricaDTO
from nsj_integracao_api_entidades.entity.persona_processosrubricas import ProcessosrubricaEntity

from nsj_integracao_api_entidades.dto.persona_processossuspensoes import ProcessossuspensoDTO
from nsj_integracao_api_entidades.entity.persona_processossuspensoes import ProcessossuspensoEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ProcessoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='processo',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    tipo: int = DTOField(
      not_null=True,)
    descricao: str = DTOField(
      not_null=True,)
    tipodecisao: int = DTOField()
    extensaodecisao: int = DTOField()
    datadecisao: datetime.datetime = DTOField()
    depositointegral: bool = DTOField()
    tipoautor: int = DTOField()
    ibge: str = DTOField()
    codigovara: str = DTOField()
    motivo: int = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    dataabertura: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    processosrubricas: list = DTOListField(
      dto_type=ProcessosrubricaDTO,
      entity_type=ProcessosrubricaEntity,
      related_entity_field='processo',
    )
    processossuspensoes: list = DTOListField(
      dto_type=ProcessossuspensoDTO,
      entity_type=ProcessossuspensoEntity,
      related_entity_field='processo',
    )
