
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.persona_intervalosjornadas import IntervalosjornadaDTO
from nsj_integracao_api_entidades.entity.persona_intervalosjornadas import IntervalosjornadaEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class JornadaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='jornada',
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
    descricao: str = DTOField(
      not_null=True,)
    entrada: datetime.time = DTOField(
      not_null=True,)
    saida: datetime.time = DTOField(
      not_null=True,)
    tipointervalo: int = DTOField(
      not_null=True,)
    duracaointervalo: int = DTOField()
    tipojornada: int = DTOField()
    descricaotipojornada: str = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    flexivel: bool = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    intervalosjornadas: list = DTOListField(
      dto_type=IntervalosjornadaDTO,
      entity_type=IntervalosjornadaEntity,
      related_entity_field='jornada',
    )
