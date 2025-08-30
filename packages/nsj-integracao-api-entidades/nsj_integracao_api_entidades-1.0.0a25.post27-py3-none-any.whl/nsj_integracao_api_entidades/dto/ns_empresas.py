
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class EmpresaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='empresa',
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
    descricao: str = DTOField()
    tipoidentificacao: int = DTOField()
    raizcnpj: str = DTOField()
    ordemcnpj: str = DTOField()
    cpf: str = DTOField()
    razaosocial: str = DTOField()
    mascaraconta: str = DTOField()
    mascaragerencial: str = DTOField()
    usadv: bool = DTOField()
    filantropica: bool = DTOField()
    cnae: str = DTOField()
    naturezajuridica: str = DTOField()
    tipopagamento: str = DTOField(
      default_value='M',)
    tipocooperativa: int = DTOField()
    tipoconstrutora: int = DTOField()
    numerocertificado: str = DTOField()
    ministerio: str = DTOField()
    dataemissaocertificado: datetime.datetime = DTOField()
    datavencimentocertificado: datetime.datetime = DTOField()
    numeroprotocolorenovacao: str = DTOField()
    dataprotocolorenovacao: datetime.datetime = DTOField()
    datapublicacaodou: datetime.datetime = DTOField()
    numeropaginadou: str = DTOField()
    nomecontato: str = DTOField()
    cpfcontato: str = DTOField()
    telefonefixocontato: str = DTOField()
    dddtelfixocontato: str = DTOField()
    telefonecelularcontato: str = DTOField()
    dddtelcelularcontato: str = DTOField()
    faxcontato: str = DTOField()
    dddfaxcontato: str = DTOField()
    emailcontato: str = DTOField()
    inativa: bool = DTOField(
      not_null=True,)
    inicioexercicio: datetime.datetime = DTOField()
    infoimagem: str = DTOField()
    grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    idweb: int = DTOField()
    inicio_atividades: datetime.datetime = DTOField()
    tributacaopiscofins: int = DTOField()
    alelonumerocontrato: int = DTOField()
    tipopontoeletronico: int = DTOField()
    multiplastabelasrubrica: bool = DTOField()
    numerosiafi: str = DTOField()
    acordointernacionalisencaomulta: bool = DTOField()
    tiposituacaopj: int = DTOField()
    tiposituacaopf: int = DTOField()
    regimeproprioprevidenciasocial: bool = DTOField()
    municipioentefederativo: str = DTOField()
    descricaoleiseguradodiferenciado: str = DTOField()
    valorsubtetoexecutivo: float = DTOField()
    valorsubtetolegislativo: float = DTOField()
    valorsubtetojudiciario: float = DTOField()
    valorsubtetotodospoderes: float = DTOField()
    anosmaioridadedependenteexecutivo: int = DTOField()
    anosmaioridadedependentelegislativo: int = DTOField()
    anosmaioridadedependentejudiciario: int = DTOField()
    anosmaioridadedependentetodospoderes: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    observacao: str = DTOField()
    regraponto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    usapontoweb: bool = DTOField()
    moeda: str = DTOField()
    perfil: str = DTOField()
    cnpjentefederativo: str = DTOField()
    empresa_multinota: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    empresadetrabalhotemporario: bool = DTOField()
    entefederativo: bool = DTOField()
    entidadeeducativa: bool = DTOField()
    esocialativo: bool = DTOField()
    importacao_hash: str = DTOField()
    numeroregistrotrabalhotemporariomte: str = DTOField()
    optantepcmso: bool = DTOField()
    optantesegurofuneral: bool = DTOField()
    optantesegurovida: bool = DTOField()
    subtetoentefederativo: int = DTOField()
    tenant_multinotas: str = DTOField()
    valorsubtetoentefederativo: float = DTOField()
    decimaiscusto: int = DTOField()

