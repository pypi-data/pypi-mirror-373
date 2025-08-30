
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ObraDTO(DTOBase):
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
    obra: int = DTOField(
      not_null=True,)
    codigonfse: str = DTOField()
    descricao: str = DTOField()
    inicio: datetime.datetime = DTOField()
    cei: str = DTOField()
    fim: datetime.datetime = DTOField()
    habite_se: datetime.datetime = DTOField()
    inativa: bool = DTOField()
    tipologradouro: str = DTOField()
    endereco: str = DTOField()
    numero: str = DTOField()
    complemento: str = DTOField()
    bairro: str = DTOField()
    municipio: str = DTOField()
    cidade: str = DTOField()
    estado: str = DTOField()
    cep: str = DTOField()
    art: str = DTOField()
    tpobra: int = DTOField()
    unidades: int = DTOField()
    upcs: int = DTOField()
    area: float = DTOField()
    aliquotarat: float = DTOField()
    aliquotafap: float = DTOField()
    cnae: str = DTOField()
    aliquotaterceiros: float = DTOField()
    cpf: str = DTOField()
    raizcnpj: str = DTOField()
    ordemcnpj: str = DTOField()
    tipoidentificacao: int = DTOField()
    contribuicaopatronalsubstituida: bool = DTOField()
    cno: str = DTOField()
    id_estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_orgao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_pessoa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_agente: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()

