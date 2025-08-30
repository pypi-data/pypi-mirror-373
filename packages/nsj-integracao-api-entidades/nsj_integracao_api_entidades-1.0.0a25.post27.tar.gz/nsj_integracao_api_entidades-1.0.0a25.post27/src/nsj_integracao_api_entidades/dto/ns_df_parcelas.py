
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DfParcelaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='parcela',
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
    id_pagamento: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    numero: str = DTOField()
    valor: float = DTOField()
    vencimento: datetime.datetime = DTOField()
    sequencial: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    conta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    usarsaldocredito: bool = DTOField()
    valorcreditoautilizar: float = DTOField()
    competencia: datetime.datetime = DTOField()
    basevencimentoparcela: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    percentual: float = DTOField()
    intervalo: int = DTOField()
    sinal: bool = DTOField(
      not_null=True,)
    valoresalteradosmanualmente: bool = DTOField(
      not_null=True,)

