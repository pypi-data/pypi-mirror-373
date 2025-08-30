
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class TabelasdeprecoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='tabeladepreco',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField(
      not_null=True,)
    desconto: int = DTOField(
      not_null=True,)
    reajuste: float = DTOField(
      not_null=True,)
    id_estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    finalidade: int = DTOField(
      not_null=True,)
    bloqueada: bool = DTOField(
      not_null=True,)
    id_empresa: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    inicioperiodo: datetime.datetime = DTOField()
    fimperiodo: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    datahoraaplicacaoreajuste: datetime.datetime = DTOField()
    dataagendamentoreajuste: datetime.datetime = DTOField()
    percentualfatorcomissao: float = DTOField()
    descontosobreprecovenda: bool = DTOField(
      not_null=True,)
    descontovalorproduto: bool = DTOField(
      not_null=True,)

