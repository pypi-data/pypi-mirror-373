
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class TipiDTO(DTOBase):
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
    ncm: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    texto: str = DTOField()
    unidade: str = DTOField()
    tipoipi: int = DTOField()
    ipi: float = DTOField()
    ipivalor: float = DTOField()
    ii: float = DTOField()
    taxadepreciacao: float = DTOField()
    descricao: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    perfil_importacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    fimvigencia: datetime.datetime = DTOField()
    unidadetributada: str = DTOField()

