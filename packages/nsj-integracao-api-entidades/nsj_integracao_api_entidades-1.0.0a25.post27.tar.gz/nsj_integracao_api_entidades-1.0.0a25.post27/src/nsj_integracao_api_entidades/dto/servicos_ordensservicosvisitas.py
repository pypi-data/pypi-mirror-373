
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class OrdensservicosvisitaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='ordemservicovisita',
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
    ordemservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    descricao: str = DTOField()
    datavisita: datetime.datetime = DTOField()
    agendado: int = DTOField()
    executado: int = DTOField()
    enderecoparticipante: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    atendimento_consecutivo: bool = DTOField()
    deslocamento: bool = DTOField()
    hora_chegada_cliente: datetime.time = DTOField()
    hora_inicio_manutencao: datetime.time = DTOField()
    hora_termino_manutencao: datetime.time = DTOField()
    parada_para_almoco: bool = DTOField()
    lastupdate: datetime.datetime = DTOField()
    hora_inicio_almoco: datetime.time = DTOField()
    hora_termino_almoco: datetime.time = DTOField()
    origem_saida: str = DTOField()
    hora_saida: datetime.time = DTOField()
    km_saida: float = DTOField()
    km_chegada_cliente: float = DTOField()
    deslocamento_extra: bool = DTOField(
      not_null=True,)
    motivo_deslocamento: str = DTOField()
    hora_saida_deslocamento: datetime.time = DTOField()
    hora_chegada_deslocamento: datetime.time = DTOField()
    km_chegada_deslocamento: float = DTOField()
    hora_saida_cliente: datetime.time = DTOField()
    veiculo_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horasexecutadas: datetime.time = DTOField()
    horasestimadas: datetime.time = DTOField()
    hora_estimada_inicio: datetime.time = DTOField()
    hora_estimada_fim: datetime.time = DTOField()

