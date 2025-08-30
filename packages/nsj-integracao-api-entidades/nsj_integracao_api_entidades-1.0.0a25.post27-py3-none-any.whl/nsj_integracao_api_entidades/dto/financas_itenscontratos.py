
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ItenscontratoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='itemcontrato',
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
    contrato: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    servico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    codigo: str = DTOField()
    observacao: str = DTOField()
    valor: float = DTOField(
      not_null=True,)
    rateio: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processado: bool = DTOField(
      not_null=True,)
    cancelado: bool = DTOField(
      not_null=True,)
    datahoracancelamento: datetime.datetime = DTOField()
    quantidade: float = DTOField(
      not_null=True,)
    objetoservicoitem: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    descontosnopedido: float = DTOField()
    unidadenatureza: int = DTOField(
      not_null=True,)
    unidadeintervalonatureza: int = DTOField(
      not_null=True,)
    quantidadeintervalonatureza: int = DTOField(
      not_null=True,)
    tipovencimento: int = DTOField(
      not_null=True,)
    diavencimento: int = DTOField(
      not_null=True,)
    adicaomesesvencimento: int = DTOField(
      not_null=True,)
    qtddiasparainicio: int = DTOField(
      not_null=True,)
    qtddiasparafim: int = DTOField(
      not_null=True,)
    qtdmesesparareajuste: int = DTOField(
      not_null=True,)
    percentualdesconto: float = DTOField(
      not_null=True,)
    percentualmulta: float = DTOField(
      not_null=True,)
    percentualjurosdiarios: float = DTOField(
      not_null=True,)
    tipocobranca: int = DTOField(
      not_null=True,)
    ultimadataprocessamento: datetime.datetime = DTOField(
      not_null=True,)
    ultimadataprocessamentotemp: datetime.datetime = DTOField()
    recorrente: bool = DTOField(
      not_null=True,)
    indice: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    dataproximoreajuste: datetime.datetime = DTOField()
    diaultimadataprocessamento: int = DTOField(
      not_null=True,)
    considerardatainicio: bool = DTOField(
      not_null=True,)
    lastupdate: datetime.datetime = DTOField()
    recorrenciapropria: bool = DTOField(
      not_null=True,)
    parcelainicial: int = DTOField(
      not_null=True,)
    parcelafinal: int = DTOField(
      not_null=True,)
    parcelaatual: int = DTOField(
      not_null=True,)
    possuicomissao: bool = DTOField(
      not_null=True,)
    retemimposto: bool = DTOField(
      not_null=True,)
    tipovalor: int = DTOField(
      not_null=True,)
    objetoservico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processaperiodoanterior: bool = DTOField(
      not_null=True,)
    dataproximaprevisao: datetime.datetime = DTOField()
    dataproximaprevisaosugerida: datetime.datetime = DTOField()
    tipoemissao: int = DTOField(
      not_null=True,)
    qtddiasemissaotitulo: int = DTOField(
      not_null=True,)
    usadiscriminacao: bool = DTOField()
    qtdtitulosagerar: int = DTOField(
      not_null=True,)
    qtdtitulosgerados: int = DTOField(
      not_null=True,)
    diaparafaturamento: int = DTOField(
      not_null=True,)
    id_item_faturamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    codigoitem: str = DTOField()
    grupofaturamento: int = DTOField(
      not_null=True,)
    reajusteautomatico: bool = DTOField(
      not_null=True,)
    # created_at: datetime.datetime = DTOField()
    # created_by: dict = DTOField()
    tiposuspensao: int = DTOField(
      not_null=True,)
    tipocomissao: int = DTOField()
    itemcontratoorigem: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    transferido: bool = DTOField()
    datafaturamento: datetime.datetime = DTOField()
    numerodiasparavencimento: int = DTOField()
    previsaovencimento: datetime.datetime = DTOField()
    evento: bool = DTOField(
      not_null=True,)
    usarindicevariavel: bool = DTOField(
      not_null=True,)
    motivocancelamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipocancelamento: int = DTOField(
      default_value=-1,)
    origemnaorecorrente: int = DTOField(
      default_value=-1,)
    situacaofaturamento: int = DTOField(
      default_value=-1,)

