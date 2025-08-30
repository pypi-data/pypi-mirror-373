
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class EventoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='evento',
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
    tipovalor: int = DTOField(
      not_null=True,)
    unidade: int = DTOField(
      not_null=True,)
    percentual: float = DTOField()
    incideinss: bool = DTOField(
      not_null=True,)
    incideirrf: bool = DTOField(
      not_null=True,)
    incidefgts: bool = DTOField(
      not_null=True,)
    categoria: int = DTOField(
      not_null=True,)
    totalizarais: bool = DTOField(
      not_null=True,)
    totalizainforme: bool = DTOField(
      not_null=True,)
    acumulahoraextra: bool = DTOField(
      not_null=True,)
    valorminimo: float = DTOField()
    valormaximo: float = DTOField()
    basefaixa: int = DTOField()
    incidepis: bool = DTOField(
      not_null=True,)
    incideencargos: bool = DTOField(
      not_null=True,)
    pagobancohoras: bool = DTOField()
    fazproporcaopiso: bool = DTOField(
      not_null=True,)
    valorpiso: float = DTOField()
    codigohomolognet: str = DTOField()
    tipomedia: int = DTOField(
      not_null=True,)
    valorintegralbasevh: bool = DTOField()
    incidedsr: bool = DTOField(
      not_null=True,)
    periodoanuenio: int = DTOField()
    qtdemaximaanuenio: int = DTOField()
    rubricaesocial: str = DTOField()
    incidesindical: bool = DTOField()
    somamediaferias: bool = DTOField()
    somamedia13: bool = DTOField()
    somamediarescisao: bool = DTOField()
    somamaiorremuneracao: bool = DTOField()
    tipocalculo: int = DTOField()
    acumulavalordia: bool = DTOField()
    valorintegralbasevalordia: bool = DTOField()
    incidesalariofamilia: bool = DTOField()
    fazproporcaocalculo: bool = DTOField()
    comparacomtarifas: bool = DTOField()
    valorintegralbasesindical: bool = DTOField()
    valorintegralbasesalariofamilia: bool = DTOField()
    incidepensaoalimenticia: bool = DTOField()
    somamediamaternidade: bool = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventofaixa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    faixa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    instituicao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipoformula: int = DTOField()
    formulabasicacondicao: str = DTOField()
    formulabasicavalor: str = DTOField()
    formulabasicareferencia: str = DTOField()
    formulaavancada: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    somentecompoemaiorremuneracao: bool = DTOField()
    valorconteudolimitealerta: float = DTOField()
    valorconteudolimiteerro: float = DTOField()
    explicacao: str = DTOField()
    informativa: bool = DTOField()
    calcularpelopercentualdoreajustesindical: bool = DTOField()
    somarbasevalorhoramaiorremuneracaorescisao: bool = DTOField()
    considerarsomentevalordocalculoatualemformulas: bool = DTOField()
    ignorarnocalculosindical: bool = DTOField()
    desabilitado: bool = DTOField(
      not_null=True,)
    id_conjunto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

