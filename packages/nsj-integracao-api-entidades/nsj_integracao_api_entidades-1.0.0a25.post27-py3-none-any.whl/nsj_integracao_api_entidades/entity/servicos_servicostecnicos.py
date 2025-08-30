
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.servicostecnicos",
    pk_field="servicotecnico",
    default_order_fields=["servicotecnico"],
)
class ServicostecnicoEntity(EntityBase):
    servicotecnico: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    bloqueado: int = None
    codigocontabil: str = None
    insspercentualincidencia: float = None
    aliquotainss: float = None
    descontocobranca: int = None
    valor: float = None
    incidecomissao: int = None
    cfop: uuid.UUID = None
    classificacaofinanceira: uuid.UUID = None
    tiposervico: uuid.UUID = None
    unidademedida: uuid.UUID = None
    servicocatalogo: uuid.UUID = None
    cor: str = None
    incluinopedidovenda: int = None
    minimohorascontratadas: int = None
    lastupdate: datetime.datetime = None
    id_grupoempresarial: uuid.UUID = None
    servicovinculado: uuid.UUID = None
    faturar: bool = None
    gerarordemdeservico: bool = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    tipo: int = None
