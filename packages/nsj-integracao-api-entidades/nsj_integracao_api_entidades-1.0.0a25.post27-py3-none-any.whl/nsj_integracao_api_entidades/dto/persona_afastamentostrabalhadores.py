
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class AfastamentostrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='afastamentotrabalhador',
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
    dias: int = DTOField()
    tipohistorico: str = DTOField()
    descricao: str = DTOField()
    observacao: str = DTOField()
    cid: str = DTOField()
    cnpjempresacessionaria: str = DTOField()
    tipoonuscessionaria: int = DTOField()
    tipoonussindicato: int = DTOField()
    tipoacidentetransito: int = DTOField()
    datainicioperiodoaquisitivo: datetime.datetime = DTOField()
    diassaldoferias: int = DTOField()
    afastamentotrabalhadorpai: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    medico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    sindicato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    estado: int = DTOField()
    dataproximasferias: datetime.datetime = DTOField()
    origem: int = DTOField()
    peloinss: bool = DTOField()
    semdataretorno: bool = DTOField()
    solicitacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
