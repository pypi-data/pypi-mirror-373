
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class AdiantamentosavulsoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='adiantamentoavulso',
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
    eventorendimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventodesconto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    historicoadiantamentoavulso: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    datacadastro: datetime.datetime = DTOField()
    valor: float = DTOField()
    observacao: str = DTOField()
    formapagamento: int = DTOField()
    mescompetencia: int = DTOField()
    anocompetencia: int = DTOField()
    situacao: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    datapagamento: datetime.datetime = DTOField()
    created_at: datetime.datetime = DTOField()
    origem: int = DTOField(
      not_null=True,)
    created_by: dict = DTOField()
    updated_by: dict = DTOField()
    numero: int = DTOField(
      not_null=True,)
    justificativa: str = DTOField()
    solicitacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

