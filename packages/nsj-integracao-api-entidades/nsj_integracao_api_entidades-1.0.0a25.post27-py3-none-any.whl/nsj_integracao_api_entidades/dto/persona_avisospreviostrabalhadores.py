
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class AvisospreviostrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='avisopreviotrabalhador',
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
    dataconcessao: datetime.datetime = DTOField(
      not_null=True,)
    dataprojetada: datetime.datetime = DTOField()
    cancelado: bool = DTOField()
    observacaoconcessao: str = DTOField()
    observacaocancelamento: str = DTOField()
    tipoconcessao: int = DTOField(
      not_null=True,)
    tipocancelamento: int = DTOField()
    datacancelamento: datetime.datetime = DTOField()
    interrompido: bool = DTOField()
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    created_by: dict = DTOField()
    created_at: datetime.datetime = DTOField()
    updated_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    situacao: int = DTOField()

