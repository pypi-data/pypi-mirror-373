
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class AdmissoespreliminareDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='admissaopreliminar',
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
    nome: str = DTOField()
    codigo: str = DTOField()
    cpf: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    dataadmissao: datetime.datetime = DTOField(
      not_null=True,)
    datanascimento: datetime.datetime = DTOField(
      not_null=True,)
    empresa: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    nivelcargo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    origem: int = DTOField()
    salariofixo: float = DTOField()
    cargo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    created_at: datetime.datetime = DTOField(
      not_null=True,)
    numero: int = DTOField(
      not_null=True,)
    departamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    created_by: dict = DTOField()
    updated_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    solicitante: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    observacao: str = DTOField()
    solicitacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

