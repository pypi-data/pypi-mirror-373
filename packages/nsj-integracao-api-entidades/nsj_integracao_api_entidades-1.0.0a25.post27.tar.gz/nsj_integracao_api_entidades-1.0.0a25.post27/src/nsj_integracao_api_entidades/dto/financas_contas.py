
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ContaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='conta',
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
    nome: str = DTOField(
      not_null=True,)
    limitenegativo: float = DTOField()
    numero: str = DTOField()
    digito: str = DTOField()
    proximocheque: str = DTOField()
    proximobordero: str = DTOField()
    bloqueado: bool = DTOField(
      not_null=True,)
    acaosaldodevedor: int = DTOField(
      not_null=True,)
    acaolimitenegativo: int = DTOField(
      not_null=True,)
    agencianumero: str = DTOField()
    agenciadigito: str = DTOField()
    agencianome: str = DTOField()
    codigocontabil: str = DTOField()
    saldo: float = DTOField(
      not_null=True,)
    limitefechamento: datetime.datetime = DTOField()
    considerasaldonofluxodecaixa: int = DTOField()
    banco: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipoconta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    codigocontabilduplicata: str = DTOField()
    usarnometitular: bool = DTOField(
      not_null=True,)
    nometitular: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    compartilhaconta: bool = DTOField(
      not_null=True,)
    id_grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_funcionario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    emprestimo: bool = DTOField(
      not_null=True,)
    layoutpagamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    chaveconciliacao: str = DTOField()
    permitirsaldonegativo: bool = DTOField()
    usarsaldominimo: bool = DTOField()
    saldominimo: float = DTOField()
    considerarsaldocheque: bool = DTOField()
    considerarsaldobordero: bool = DTOField()
    id_layoutimpressoracheque: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    layoutcobranca: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_pessoa_emprestimo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_estabelecimento_emprestimo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    banconumero: str = DTOField()
    tipocontaemprestimo: int = DTOField()
    nomegerente: str = DTOField()
    considerarsaldoaviso: bool = DTOField()
    possuichequeespecial: bool = DTOField()
    chequeespecial: float = DTOField()
    contapadrao: bool = DTOField()
    cpfcnpjtitular: str = DTOField()

