
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class OrdensservicositenDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='ordemservicoitem',
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
    ordemservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    servicotecnico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    objetoservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horascontratadas: int = DTOField()
    horasexecutadas: int = DTOField()
    horasfaturar: int = DTOField()
    servicoexecutado: int = DTOField()
    descontopercentual: float = DTOField()
    valortotal: float = DTOField()
    lastupdate: datetime.datetime = DTOField()
    valorunitario: float = DTOField()
    created_at: datetime.datetime = DTOField()
    updated_at: datetime.datetime = DTOField()
    created_by: dict = DTOField()
    updated_by: dict = DTOField()
    diastrabalhados: int = DTOField()
    quantidadeutilizada: int = DTOField()
    horasutilizadas: float = DTOField()
    projetoitemescopo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horas_prevista_execucao: int = DTOField()
    datainiciomanutencao: datetime.datetime = DTOField()
    dataterminomanutencao: datetime.datetime = DTOField()

