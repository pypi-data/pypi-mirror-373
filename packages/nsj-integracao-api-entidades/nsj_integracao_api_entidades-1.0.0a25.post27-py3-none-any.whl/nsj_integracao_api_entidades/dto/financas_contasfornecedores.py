
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ContasfornecedoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='contafornecedor',
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
    banco: str = DTOField()
    agencianumero: str = DTOField()
    agenciadv: str = DTOField()
    agencianome: str = DTOField()
    contanumero: str = DTOField()
    contadv: str = DTOField()
    tipoconta: int = DTOField()
    id_fornecedor: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    padrao: bool = DTOField()
    excluida: bool = DTOField()
    lastupdate: datetime.datetime = DTOField()

