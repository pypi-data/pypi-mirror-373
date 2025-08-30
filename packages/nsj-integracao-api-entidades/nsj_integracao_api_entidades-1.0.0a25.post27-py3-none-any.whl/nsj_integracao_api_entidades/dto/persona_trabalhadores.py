
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.persona_outrosrecebimentostrabalhadores import OutrosrecebimentostrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_outrosrecebimentostrabalhadores import OutrosrecebimentostrabalhadoreEntity

from nsj_integracao_api_entidades.dto.persona_outrosrendimentostrabalhadores import OutrosrendimentostrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_outrosrendimentostrabalhadores import OutrosrendimentostrabalhadoreEntity

from nsj_integracao_api_entidades.dto.persona_gestorestrabalhadores import GestorestrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_gestorestrabalhadores import GestorestrabalhadoreEntity

from nsj_integracao_api_entidades.dto.persona_valestransportespersonalizadostrabalhadores import ValestransportespersonalizadostrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_valestransportespersonalizadostrabalhadores import ValestransportespersonalizadostrabalhadoreEntity

from nsj_integracao_api_entidades.dto.persona_horariosalternativostrabalhadores import HorariosalternativostrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_horariosalternativostrabalhadores import HorariosalternativostrabalhadoreEntity

from nsj_integracao_api_entidades.dto.persona_avisospreviostrabalhadores import AvisospreviostrabalhadoreDTO
from nsj_integracao_api_entidades.entity.persona_avisospreviostrabalhadores import AvisospreviostrabalhadoreEntity

# from nsj_integracao_api_entidades.dto.ponto_pendenciascalculostrabalhadores import PendenciascalculostrabalhadoreDTO
# from nsj_integracao_api_entidades.entity.ponto_pendenciascalculostrabalhadores import PendenciascalculostrabalhadoreEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class TrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='trabalhador',
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
    tipo: int = DTOField(
      not_null=True,)
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    nome: str = DTOField()
    dataadmissao: datetime.datetime = DTOField()
    tipoadmissao: int = DTOField()
    primeiroemprego: bool = DTOField()
    tiporegimetrabalhista: int = DTOField()
    tiporegimeinss: int = DTOField()
    tipoatividade: int = DTOField()
    salariofixo: float = DTOField()
    salariovariavel: float = DTOField()
    unidadesalariofixo: int = DTOField()
    unidadesalariovariavel: int = DTOField()
    tipocontrato: int = DTOField()
    datafimcontrato: datetime.datetime = DTOField()
    diasexperienciacontrato: int = DTOField()
    diasprorrogacaocontrato: int = DTOField()
    numerohorasmensais: float = DTOField()
    numerodiasperiodo: int = DTOField()
    numerocontasalario: str = DTOField()
    numerocontasalariodv: str = DTOField()
    numerocontafgts: str = DTOField()
    tiporecebimentosalario: int = DTOField()
    dataopcaofgts: datetime.datetime = DTOField()
    optantefgts: bool = DTOField()
    categoriatrabalhador: str = DTOField()
    numeroreciborescisao: str = DTOField()
    datarescisao: datetime.datetime = DTOField()
    motivorescisao: str = DTOField()
    tiporeintegracao: int = DTOField()
    numeroleianistia: str = DTOField()
    datareintegracaoretroativa: datetime.datetime = DTOField()
    datareintegracaoretorno: datetime.datetime = DTOField()
    raca: str = DTOField()
    grauinstrucao: str = DTOField()
    paisnacionalidade: str = DTOField()
    sexo: int = DTOField()
    estadocivil: int = DTOField()
    datanascimento: datetime.datetime = DTOField()
    ufnascimento: str = DTOField()
    cidadenascimento: str = DTOField()
    municipionascimento: str = DTOField()
    paisnascimento: str = DTOField()
    nomepai: str = DTOField()
    nomemae: str = DTOField()
    datachegadapais: datetime.datetime = DTOField()
    datanaturalizacao: datetime.datetime = DTOField()
    casadocombrasileiro: bool = DTOField()
    filhobrasileiro: bool = DTOField()
    deficientevisual: bool = DTOField()
    deficienteauditivo: bool = DTOField()
    reabilitado: bool = DTOField()
    numeroctps: str = DTOField()
    seriectps: str = DTOField()
    ufctps: str = DTOField()
    dataexpedicaoctps: datetime.datetime = DTOField()
    numeroric: str = DTOField()
    orgaoemissorric: str = DTOField()
    dataexpedicaoric: datetime.datetime = DTOField()
    ufric: str = DTOField()
    cidaderic: str = DTOField()
    numerorg: str = DTOField()
    orgaoemissorrg: str = DTOField()
    dataexpedicaorg: datetime.datetime = DTOField()
    ufrg: str = DTOField()
    numerooc: str = DTOField()
    orgaoemissoroc: str = DTOField()
    dataexpedicaooc: datetime.datetime = DTOField()
    datavalidadeoc: datetime.datetime = DTOField()
    numerocnh: str = DTOField()
    orgaoemissorcnh: str = DTOField()
    dataexpedicaocnh: datetime.datetime = DTOField()
    datavalidadecnh: datetime.datetime = DTOField()
    dataprimeirahabilitacaocnh: datetime.datetime = DTOField()
    categoriacnh: int = DTOField()
    paisemissaopassaporte: str = DTOField()
    numeropassaporte: str = DTOField()
    orgaoemissorpassaporte: str = DTOField()
    ufpassaporte: str = DTOField()
    dataexpedicaopassaporte: datetime.datetime = DTOField()
    datavalidadepassaporte: datetime.datetime = DTOField()
    cpf: str = DTOField()
    nis: str = DTOField()
    numeronaturalizacao: str = DTOField()
    numerote: str = DTOField()
    zonate: int = DTOField()
    secaote: int = DTOField()
    ufte: str = DTOField()
    numeroatestadoobito: str = DTOField()
    datavencimentoatestadomedico: datetime.datetime = DTOField()
    tipocertidao: int = DTOField()
    numerocertidao: str = DTOField()
    livrocertidao: str = DTOField()
    folhacertidao: str = DTOField()
    dataexpedicaocertidao: datetime.datetime = DTOField()
    cidadecertidao: str = DTOField()
    ufcertidao: str = DTOField()
    cartoriocertidao: str = DTOField()
    numerocr: str = DTOField()
    dataexpedicaocr: datetime.datetime = DTOField()
    seriecr: str = DTOField()
    tipologradouro: str = DTOField()
    municipioresidencia: str = DTOField()
    paisresidencia: str = DTOField()
    logradouro: str = DTOField()
    numero: str = DTOField()
    complemento: str = DTOField()
    bairro: str = DTOField()
    cidade: str = DTOField()
    cep: str = DTOField()
    residenciapropria: bool = DTOField()
    usoufgtscompraimovel: bool = DTOField()
    telefone: str = DTOField()
    email: str = DTOField()
    saldoferias: int = DTOField()
    inicioperiodoaquisitivoferias: datetime.datetime = DTOField()
    dataproximasferias: datetime.datetime = DTOField()
    saldofgts: float = DTOField()
    percentualadiantamento: float = DTOField()
    descontainss: bool = DTOField()
    tinhaempregonoaviso: bool = DTOField()
    sindicalizado: bool = DTOField()
    datainicioanuenio: datetime.datetime = DTOField()
    jornadareduzida: bool = DTOField()
    teveavisoindenizado: bool = DTOField()
    fgtsmesanteriorrescisaorecolhido: bool = DTOField()
    agentenocivo: str = DTOField()
    numerocartaovt: str = DTOField()
    diasemanacommeiovt: int = DTOField()
    observacao: str = DTOField()
    cnpjempresaanterior: str = DTOField()
    matriculaempresaanterior: str = DTOField()
    dataadmissaoempresaanterior: datetime.datetime = DTOField()
    cnpjcendente: str = DTOField()
    matriculacedente: str = DTOField()
    dataadmissaocedente: datetime.datetime = DTOField()
    cnpjempresasucessora: str = DTOField()
    trabalhaemoutraempresa: bool = DTOField()
    ordemcalculoinssfolha: int = DTOField()
    ordemcalculoinss13: int = DTOField()
    simplesconcomitante: str = DTOField()
    dddtel: str = DTOField()
    sangue: int = DTOField()
    ordemcalculoduplovinculo: int = DTOField()
    cbo: str = DTOField()
    deficienteintelectual: bool = DTOField()
    deficientemental: bool = DTOField()
    motivoadmissao: int = DTOField()
    quantidademediahorassemanais: float = DTOField()
    motivocontratacaotemporaria: int = DTOField()
    avisoindenizadopago: bool = DTOField()
    dataprojecaoavisopreviopago: datetime.datetime = DTOField()
    recolheufgtsmesanterior: bool = DTOField()
    regimedejornada: int = DTOField()
    mesestrabalhadosoutrasempresas: int = DTOField()
    infoimagem: str = DTOField()
    deficientefisico: bool = DTOField()
    agencia: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
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
    acordodeprorrogacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    matriculaoutracategoria: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    departamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    matriculaoutrovinculo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    trabalhadorsubstituido: uuid.UUID = DTOField(
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
    nivelcargo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processoreintegracao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processoadmissao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processodemissao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processoirrf: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processoinss: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processomenoraprendiz: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    sindicato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipofuncionario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    identificacaonasajon: str = DTOField()
    vinculo: str = DTOField()
    status: int = DTOField()
    avaliador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    gestor: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadacumpridasemanademissao: bool = DTOField()
    jornadasabadocompensadasemanademissao: bool = DTOField()
    funcao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    cageddiariogerado: bool = DTOField()
    nivelestagio: int = DTOField()
    areaatuacaoestagio: str = DTOField()
    apoliceseguroestagio: str = DTOField()
    nomesupervisorestagio: str = DTOField()
    cpfsupervisorestagio: str = DTOField()
    estagioobrigatorio: bool = DTOField()
    instituicaoensino: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    instituicaointegradora: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    percentualdeducaobaseirrf: float = DTOField()
    percentualdeducaobaseinss: float = DTOField()
    aliquotaiss: float = DTOField()
    motivodesligamentodiretor: str = DTOField()
    datatransferencia: datetime.datetime = DTOField()
    empresaanterior: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    trabalhadorempresaanterior: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    trabalhadorcontratoanterior: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    subtipo: int = DTOField()
    valorgratificacoesrescisao: float = DTOField()
    valorbancohorasrescisao: float = DTOField()
    mesesbancohorasrescisao: int = DTOField()
    mesesgratificacoesrescisao: int = DTOField()
    motivodispensavt: str = DTOField()
    excluido: bool = DTOField()
    celular: str = DTOField()
    dddcel: str = DTOField()
    datafimmarcacaoponto: datetime.datetime = DTOField()
    identidadecorporativa: str = DTOField()
    dddtelcorporativo: str = DTOField()
    telefonecorporativo: str = DTOField()
    ramalcorporativo: str = DTOField()
    senhapontoweb: str = DTOField()
    dataprorrogacaocontrato: datetime.datetime = DTOField()
    descontacontribuicaosindical: bool = DTOField()
    informousaldoinicialbhesocial: bool = DTOField()
    descontavaletransporte: bool = DTOField()
    clausulanaopagamentomultaantecipacaofimcontrato: bool = DTOField()
    dataultimaatualizacaosaldofgts: datetime.datetime = DTOField()
    periodoapuracaopontoproprio: bool = DTOField()
    horarionoturnojornadasemanal: bool = DTOField()
    chavepix: str = DTOField()
    ufcnh: str = DTOField()
    descricaosalariovariavel: str = DTOField()
    tipoinclusaotemporaria: int = DTOField()
    cpftrabalhadorsubstituido: str = DTOField()
    temporesidenciaestrangeiro: int = DTOField()
    classificacaoestrangeiro: int = DTOField()
    condicaoambientetrabalho: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    matriculaesocial: str = DTOField()
    # Atributos de lista
    outrosrecebimentostrabalhadores: list = DTOListField(
      dto_type=OutrosrecebimentostrabalhadoreDTO,
      entity_type=OutrosrecebimentostrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    outrosrendimentostrabalhadores: list = DTOListField(
      dto_type=OutrosrendimentostrabalhadoreDTO,
      entity_type=OutrosrendimentostrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    gestorestrabalhadores: list = DTOListField(
      dto_type=GestorestrabalhadoreDTO,
      entity_type=GestorestrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    valestransportespersonalizadostrabalhadores: list = DTOListField(
      dto_type=ValestransportespersonalizadostrabalhadoreDTO,
      entity_type=ValestransportespersonalizadostrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    horariosalternativostrabalhadores: list = DTOListField(
      dto_type=HorariosalternativostrabalhadoreDTO,
      entity_type=HorariosalternativostrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    avisospreviostrabalhadores: list = DTOListField(
      dto_type=AvisospreviostrabalhadoreDTO,
      entity_type=AvisospreviostrabalhadoreEntity,
      related_entity_field='trabalhador',
    )
    # pendenciascalculostrabalhadores: list = DTOListField(
    #   dto_type=PendenciascalculostrabalhadoreDTO,
    #   entity_type=PendenciascalculostrabalhadoreEntity,
    #   related_entity_field='trabalhador',
    #   use_integrity_check=False
    # )
