
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class CargoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='cargo',
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
    descricao: str = DTOField()
    cbo: str = DTOField()
    experiencia: str = DTOField()
    grauinstrucao: str = DTOField()
    maiorsalmercado: float = DTOField()
    menorsalmercado: float = DTOField()
    requisitos: str = DTOField()
    diasexperienciacontrato: int = DTOField()
    diasprorrogacaocontrato: int = DTOField()
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
    departamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lotacao: uuid.UUID = DTOField(
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
    pontuacao: float = DTOField()
    contagemespecial: int = DTOField()
    dedicacaoexclusiva: bool = DTOField()
    dataleicargo: datetime.datetime = DTOField()
    numeroleicargo: str = DTOField()
    situacaoleicargo: int = DTOField()
    pisominimo: float = DTOField()
    cargopublico: bool = DTOField()
    acumulacaocargos: int = DTOField()
    desabilitado: bool = DTOField(
      not_null=True,)
    importacao_hash: str = DTOField()
    condicaoambientetrabalho: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

