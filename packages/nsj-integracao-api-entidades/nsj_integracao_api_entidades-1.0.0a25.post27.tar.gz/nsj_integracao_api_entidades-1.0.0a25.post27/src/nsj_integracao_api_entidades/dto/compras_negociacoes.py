
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class NegociacoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='negociacao',
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
    usuarioresponsavel: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    requisicaocompra: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    valorprodutosservicos: float = DTOField()
    valorfrete: float = DTOField()
    valoroutrasdespesas: float = DTOField()
    valortotal: float = DTOField()
    status: int = DTOField()
    datahoraabertura: datetime.datetime = DTOField()
    datahoraprocessamento: datetime.datetime = DTOField()
    estabelecimento: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    numero: int = DTOField(
      not_null=True,)
    lastupdate: datetime.datetime = DTOField()
    valortributos: float = DTOField()
    wkf_estado: str = DTOField()
    wkf_data: datetime.datetime = DTOField()
    localdeuso: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

