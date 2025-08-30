
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_linhas_impostos",
    pk_field="df_linha_imposto",
    default_order_fields=["df_linha_imposto"],
)
class DfLinhaImpostoEntity(EntityBase):
    df_linha_imposto: uuid.UUID = None
    tenant: int = None
    df_linha: uuid.UUID = None
    valorsituacaotributariaicms: float = None
    valororigemmercadoriaicms: float = None
    valoraliquotacreditoicms: float = None
    valorcreditoicms: float = None
    valorpercentualreducaoicms: float = None
    valorbaseicms: float = None
    valoraliquotaicms: float = None
    valoricms: float = None
    valorformacobrancaicmsst: float = None
    valorbaseretidaicmsst: float = None
    valorretidoicmsst: float = None
    valorpercentualmvaicmsst: float = None
    valorpercentualreducaoicmsst: float = None
    valorbaseicmsst: float = None
    valoraliquotaicmsst: float = None
    valoricmsst: float = None
    valortipotributacaoipi: float = None
    valorbaseipi: float = None
    valoraliquotaipi: float = None
    valoripi: float = None
    valortipotributacaopis: float = None
    valorbasepis: float = None
    valoraliquotapis: float = None
    valorpis: float = None
    valortipotributacaocofins: float = None
    valorbasecofins: float = None
    valoraliquotacofins: float = None
    valorcofins: float = None
    lastupdate: datetime.datetime = None
    valorbaseii: float = None
    valoraliquotaii: float = None
    valorii: float = None
    valorpercentualfcpicmsdestino: float = None
    valoraliquotainternaicmsdestino: float = None
    valorpercentualpartilhaicmsdestino: float = None
    valorfcpicmsdestino: float = None
    valoricmsdestino: float = None
    valoricmsinterestadualorigem: float = None
    valoraliquotainterestadualicmsdestino: float = None
    incidencia_ipi: int = None
    motivodesoneracao: int = None
    percentual_diferimento: float = None
    pfcp: float = None
    pfcpst: float = None
    pfcpstret: float = None
    picmsefet: float = None
    predbcefet: float = None
    pst: float = None
    valor_diferimento: float = None
    valoraduaneiro: float = None
    valorbaseicmsdestino: float = None
    valordesoneracao: float = None
    valoricms_sem_diferimento: float = None
    valornaoretidoicmsst: float = None
    vbcefet: float = None
    vbcfcp: float = None
    vbcfcpst: float = None
    vbcfcpstret: float = None
    vbcfcpufdest: float = None
    vfcp: float = None
    vfcpst: float = None
    vfcpstret: float = None
    vicmsefet: float = None
