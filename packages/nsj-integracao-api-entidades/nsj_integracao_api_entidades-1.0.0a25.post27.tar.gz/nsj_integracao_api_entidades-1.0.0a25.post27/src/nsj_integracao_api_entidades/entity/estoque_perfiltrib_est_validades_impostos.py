
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.perfiltrib_est_validades_impostos",
    pk_field="perfiltrib_est_validade_imposto",
    default_order_fields=["perfiltrib_est_validade_imposto"],
)
class PerfiltribEstValidadeImpostoEntity(EntityBase):
    perfiltrib_est_validade_imposto: uuid.UUID = None
    tenant: int = None
    perfiltrib_est_validade: uuid.UUID = None
    uf_destino: str = None
    icms_cst: int = None
    icms_reducao: float = None
    mva: float = None
    icms_reducao_st: float = None
    icms_reducao_st_simples: float = None
    icms_formadecobranca_st: int = None
    icms_baseminima: float = None
    icms_entrada: float = None
    icms_saida: float = None
    icms_csosn: int = None
    lastupdate: datetime.datetime = None
    icms_csosn_contribuinte: int = None
    fcp: float = None
    diferimento: float = None
    modalidade_bc_icmsst: int = None
    modalidade_bc_icms: int = None
    icms_cst_contribuinte: int = None
