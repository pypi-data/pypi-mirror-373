
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class SindicatoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='sindicato',
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
    logradouro: str = DTOField()
    numero: str = DTOField()
    complemento: str = DTOField()
    bairro: str = DTOField()
    cidade: str = DTOField()
    cep: str = DTOField()
    codigocontribuicao: str = DTOField()
    cnpj: str = DTOField()
    codigoentidadesindical: str = DTOField()
    pisosalarial: float = DTOField()
    calculoeacumulativo: bool = DTOField()
    estado: str = DTOField()
    calculanofim: bool = DTOField()
    patronal: bool = DTOField()
    contato: str = DTOField()
    telefone: str = DTOField()
    dddtel: str = DTOField()
    fax: str = DTOField()
    dddfax: str = DTOField()
    email: str = DTOField()
    somentemaioranuenio: bool = DTOField()
    multafgts: float = DTOField()
    mesesmediamaternidade: int = DTOField()
    diadissidio: int = DTOField()
    diasaviso: int = DTOField()
    qtdemrre: int = DTOField()
    qtdemrfe: int = DTOField()
    qtdemr13: int = DTOField()
    mesassistencial: int = DTOField()
    mediaferiaspelomaiorvalor: bool = DTOField()
    media13pelomaiorvalor: bool = DTOField()
    mediarescisaopelomaiorvalor: bool = DTOField()
    mesdesconto: int = DTOField()
    mesdissidio: int = DTOField()
    mesesmediaferias: int = DTOField()
    mesesmediarescisao: int = DTOField()
    mesesmedia13: int = DTOField()
    numeradorfracao: int = DTOField()
    denominadorfracao: int = DTOField()
    fpas: str = DTOField()
    codigoterceiros: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    regraponto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

