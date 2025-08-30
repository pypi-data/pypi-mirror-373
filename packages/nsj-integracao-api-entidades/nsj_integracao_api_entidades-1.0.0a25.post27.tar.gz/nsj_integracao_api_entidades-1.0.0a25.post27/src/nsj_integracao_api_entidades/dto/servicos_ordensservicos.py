
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class OrdensservicoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='ordemservico',
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
    data_criacao: datetime.datetime = DTOField()
    hora_criacao: datetime.time = DTOField()
    chamadotecnico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    situacao: int = DTOField()
    referenciaexterna: str = DTOField()
    tipoordemservico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    ordemservicoretorno_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    origem: int = DTOField()
    estabelecimento_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    cliente_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    objetoservico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    enderecocliente_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    valor_total: float = DTOField()
    xml_docengine: str = DTOField()
    contrato_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipo_manutencao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    situacao_maquina_chamado: int = DTOField()
    sintoma: str = DTOField()
    situacao_maquina_chegada: int = DTOField()
    causa: str = DTOField()
    situacao_maquina_saida: int = DTOField()
    intervencao: str = DTOField()
    observacao: str = DTOField()
    horimetro: float = DTOField()
    numero: int = DTOField(
      not_null=True,)
    usuario_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    assinado_por: str = DTOField()
    orcamento_gerado: bool = DTOField(
      not_null=True,)
    numero_orcamento: int = DTOField()
    responsavel_orcamento: str = DTOField()
    pedido_garantia: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    tabeladepreco_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    operacaoordemservico_codigo: str = DTOField()
    operacaoordemservico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    ordemservicovinculada: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    pessoamunicipio: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    created_at: datetime.datetime = DTOField()
    updated_at: datetime.datetime = DTOField()
    projeto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    rascunho: bool = DTOField()
    created_by: dict = DTOField()
    updated_by: dict = DTOField()
    grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    serie: str = DTOField()
    motivofinalizacao: str = DTOField()
    tipologradouro: str = DTOField()
    pais: str = DTOField()
    ibge: str = DTOField()
    logradouro: str = DTOField()
    numeroendereco: str = DTOField()
    complemento: str = DTOField()
    cep: str = DTOField()
    bairro: str = DTOField()
    uf: str = DTOField()
    cidade: str = DTOField()
    latitude: float = DTOField()
    longitude: float = DTOField()
    cidadeestrangeira: str = DTOField()
    numeronegocio: str = DTOField()
    enderecoorigem: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lote: int = DTOField()

