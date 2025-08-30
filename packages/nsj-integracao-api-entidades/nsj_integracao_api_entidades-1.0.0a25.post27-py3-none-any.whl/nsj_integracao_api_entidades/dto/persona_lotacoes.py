
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class LotacoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='lotacao',
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
    nome: str = DTOField()
    tipo: int = DTOField()
    enderecodiferente: bool = DTOField()
    tipologradouro: str = DTOField()
    logradouro: str = DTOField()
    numero: str = DTOField()
    complemento: str = DTOField()
    bairro: str = DTOField()
    cidade: str = DTOField()
    cep: str = DTOField()
    uf: str = DTOField()
    municipio: str = DTOField()
    centrocustonasajon: int = DTOField()
    classefinnasajon: int = DTOField()
    ccustopersona: str = DTOField()
    classefinpersona: str = DTOField()
    outrasentidadesdiferente: bool = DTOField()
    fpas: str = DTOField()
    codigoterceiros: str = DTOField()
    aliquotaterceiros: float = DTOField()
    agentenocivo: str = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tomador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    obra: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    nuncaexpostoagentenocivo: bool = DTOField()
    regraponto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    bancohoras: bool = DTOField()
    desabilitado: bool = DTOField()

