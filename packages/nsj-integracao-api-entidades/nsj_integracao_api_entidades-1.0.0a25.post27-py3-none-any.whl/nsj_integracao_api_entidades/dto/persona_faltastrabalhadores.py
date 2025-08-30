
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class FaltastrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='faltatrabalhador',
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
    data: datetime.datetime = DTOField()
    descricao: str = DTOField()
    tipo: int = DTOField(
      not_null=True,)
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    descontaponto: bool = DTOField()
    status: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    responsavel: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    solicitante: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    datacriacao: datetime.datetime = DTOField()
    datamudancaestado: datetime.datetime = DTOField()
    emailresponsavel: str = DTOField()
    observacao: str = DTOField()
    compensacao: bool = DTOField()
    origem: int = DTOField()
    mesdescontocalculo: int = DTOField()
    anodescontocalculo: int = DTOField()
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    solicitacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    descontavr: bool = DTOField()
    descontavt: bool = DTOField()
    descontava: bool = DTOField()

