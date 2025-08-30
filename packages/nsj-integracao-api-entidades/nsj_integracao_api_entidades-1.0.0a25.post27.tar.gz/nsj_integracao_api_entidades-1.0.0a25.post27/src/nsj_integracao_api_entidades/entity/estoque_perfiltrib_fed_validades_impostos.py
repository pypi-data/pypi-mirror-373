
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.perfiltrib_fed_validades_impostos",
    pk_field="perfiltrib_fed_validade_imposto",
    default_order_fields=["perfiltrib_fed_validade_imposto"],
)
class PerfiltribFedValidadeImpostoEntity(EntityBase):
    perfiltrib_fed_validade_imposto: uuid.UUID = None
    tenant: int = None
    perfiltrib_fed_validade: uuid.UUID = None
    ipi_cst_entrada: int = None
    ipi_aliquota: float = None
    pis_cst: int = None
    pis_aliquota: float = None
    cofins_cst: int = None
    cofins_aliquota: float = None
    piscofins_sped: uuid.UUID = None
    piscofins_dacon: uuid.UUID = None
    unidadetributavel_quantidade: float = None
    unidadetributavel_unidade: uuid.UUID = None
    ipi_cst_saida: int = None
    lastupdate: datetime.datetime = None
