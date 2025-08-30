
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class BeneficioDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='beneficio',
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
    descricao: str = DTOField()
    tipovalor: int = DTOField(
      not_null=True,)
    tipobasevalor: int = DTOField()
    valor: float = DTOField()
    proporcionalizavalor: bool = DTOField()
    tipodesconto: int = DTOField(
      not_null=True,)
    tipobasedesconto: int = DTOField()
    tipoaplicacaodesconto: int = DTOField()
    valordesconto: float = DTOField()
    tipoformulavalor: int = DTOField()
    tipoformuladesconto: int = DTOField()
    formulabasicacondicaovalor: str = DTOField()
    formulabasicacondicaodesconto: str = DTOField()
    formulabasicavalor: str = DTOField()
    formulabasicadesconto: str = DTOField()
    formulaavancadavalor: str = DTOField()
    formulaavancadadesconto: str = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventodesconto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    faixavalor: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    faixadesconto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipobeneficio: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    permitedependente: bool = DTOField()
    tipobeneficiointerno: int = DTOField()

