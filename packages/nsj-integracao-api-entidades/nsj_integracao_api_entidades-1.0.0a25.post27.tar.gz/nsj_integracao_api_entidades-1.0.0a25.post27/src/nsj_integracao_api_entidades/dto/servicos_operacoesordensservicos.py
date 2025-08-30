
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class OperacoesordensservicoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='operacaoordemservico',
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
    codigo: str = DTOField()
    descricao: str = DTOField()
    ativo: bool = DTOField()
    referenciaexterna: bool = DTOField()
    ordemservicoretorno: bool = DTOField()
    chamadotecnico: bool = DTOField()
    campodetalheinstancia: str = DTOField()
    horimetro: bool = DTOField()
    contrato: bool = DTOField()
    sintoma: bool = DTOField()
    causa: bool = DTOField()
    intervencao: bool = DTOField()
    orcamento: bool = DTOField()
    assinadopor: bool = DTOField()
    materiais: bool = DTOField()
    gerarequisicao: bool = DTOField()
    documentorequisicao_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    geranotafiscal: bool = DTOField()
    documentonotafiscal_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estimativadehoras: bool = DTOField()
    saidaparacliente: bool = DTOField()
    chegadanocliente: bool = DTOField()
    saidadocliente: bool = DTOField()
    deslocamentoextra: bool = DTOField()
    veiculo: bool = DTOField(
      not_null=True,)
    faturamento: bool = DTOField()
    faturaservico: bool = DTOField()
    faturavisita: bool = DTOField()
    tipoordemservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipomanutencao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    utilizadevolviveis: bool = DTOField()
    documentodevolvivelsaida_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    participante_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tiporeajuste: int = DTOField(
      not_null=True,)
    valorpercentualreajuste: float = DTOField(
      not_null=True,)
    documentodevolvivelentrada_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    gerarentradadevolvivel: bool = DTOField()
    sinaldocumentovalordevolvivel: int = DTOField(
      not_null=True,
      default_value=-1,)
    validade: str = DTOField()
    tempoaviso: str = DTOField()
    projeto: bool = DTOField()
    utiliza_tipo_manutencao: bool = DTOField()
    visita: bool = DTOField(
      not_null=True,)
    encerrar_ao_executar_visita: bool = DTOField(
      not_null=True,)
    utiliza_centrocusto_os: bool = DTOField()
    created_at: datetime.datetime = DTOField()
    created_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    updated_by: dict = DTOField()
    objetoservico: bool = DTOField()
    textoconformativo: str = DTOField()
    rateiopadrao: str = DTOField()

