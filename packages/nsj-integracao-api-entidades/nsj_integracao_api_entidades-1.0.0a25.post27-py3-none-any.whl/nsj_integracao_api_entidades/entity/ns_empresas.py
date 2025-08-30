
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.empresas",
    pk_field="empresa",
    default_order_fields=["codigo"],
)
class EmpresaEntity(EntityBase):
    empresa: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipoidentificacao: int = None
    raizcnpj: str = None
    ordemcnpj: str = None
    cpf: str = None
    razaosocial: str = None
    mascaraconta: str = None
    mascaragerencial: str = None
    usadv: bool = None
    filantropica: bool = None
    cnae: str = None
    naturezajuridica: str = None
    tipopagamento: str = None
    tipocooperativa: int = None
    tipoconstrutora: int = None
    numerocertificado: str = None
    ministerio: str = None
    dataemissaocertificado: datetime.datetime = None
    datavencimentocertificado: datetime.datetime = None
    numeroprotocolorenovacao: str = None
    dataprotocolorenovacao: datetime.datetime = None
    datapublicacaodou: datetime.datetime = None
    numeropaginadou: str = None
    nomecontato: str = None
    cpfcontato: str = None
    telefonefixocontato: str = None
    dddtelfixocontato: str = None
    telefonecelularcontato: str = None
    dddtelcelularcontato: str = None
    faxcontato: str = None
    dddfaxcontato: str = None
    emailcontato: str = None
    inativa: bool = None
    inicioexercicio: datetime.datetime = None
    infoimagem: str = None
    grupoempresarial: uuid.UUID = None
    idweb: int = None
    inicio_atividades: datetime.datetime = None
    tributacaopiscofins: int = None
    alelonumerocontrato: int = None
    tipopontoeletronico: int = None
    multiplastabelasrubrica: bool = None
    numerosiafi: str = None
    acordointernacionalisencaomulta: bool = None
    tiposituacaopj: int = None
    tiposituacaopf: int = None
    regimeproprioprevidenciasocial: bool = None
    municipioentefederativo: str = None
    descricaoleiseguradodiferenciado: str = None
    valorsubtetoexecutivo: float = None
    valorsubtetolegislativo: float = None
    valorsubtetojudiciario: float = None
    valorsubtetotodospoderes: float = None
    anosmaioridadedependenteexecutivo: int = None
    anosmaioridadedependentelegislativo: int = None
    anosmaioridadedependentejudiciario: int = None
    anosmaioridadedependentetodospoderes: int = None
    lastupdate: datetime.datetime = None
    observacao: str = None
    regraponto: uuid.UUID = None
    usapontoweb: bool = None
    moeda: str = None
    perfil: str = None
    cnpjentefederativo: str = None
    empresa_multinota: uuid.UUID = None
    empresadetrabalhotemporario: bool = None
    entefederativo: bool = None
    entidadeeducativa: bool = None
    esocialativo: bool = None
    importacao_hash: str = None
    numeroregistrotrabalhotemporariomte: str = None
    optantepcmso: bool = None
    optantesegurofuneral: bool = None
    optantesegurovida: bool = None
    subtetoentefederativo: int = None
    tenant_multinotas: str = None
    valorsubtetoentefederativo: float = None
    decimaiscusto: int = None
