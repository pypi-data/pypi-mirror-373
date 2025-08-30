
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ContatoDTO(DTOBase):
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
    nome: str = DTOField()
    nascimento: datetime.datetime = DTOField()
    cargo: str = DTOField()
    sexomasculino: bool = DTOField()
    observacao: str = DTOField()
    email: str = DTOField()
    primeironome: str = DTOField()
    sobrenome: str = DTOField()
    id_pessoa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    principal: bool = DTOField()
    cpf: str = DTOField()
    responsavellegal: bool = DTOField(
      not_null=True,)
    decisor: bool = DTOField()
    influenciador: bool = DTOField()

