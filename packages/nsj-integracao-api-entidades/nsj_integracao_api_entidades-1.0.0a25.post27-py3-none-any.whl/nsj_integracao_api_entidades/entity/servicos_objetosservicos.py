
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.objetosservicos",
    pk_field="objetoservico",
    default_order_fields=["objetoservico"],
)
class ObjetosservicoEntity(EntityBase):
    objetoservico: uuid.UUID = None
    tenant: int = None
    tipo: str = None
    nome: str = None
    codigo: str = None
    participante: uuid.UUID = None
    id_contrato: uuid.UUID = None
    origem: int = None
    numero_serie: str = None
    garantia: bool = None
    data_inicio_garantia: datetime.datetime = None
    data_fim_garantia: datetime.datetime = None
    tipo_id: uuid.UUID = None
    modelo_id: uuid.UUID = None
    lastupdate: datetime.datetime = None
    endereco_id: uuid.UUID = None
    detentor_id: uuid.UUID = None
    pessoamunicipio: uuid.UUID = None
    proprietario_id: uuid.UUID = None
    proprietario_tipo: int = None
    detentor_tipo: int = None
    municipio: str = None
    id_capitulo: uuid.UUID = None
    ativa: bool = None
    situacao: int = None
    produto: uuid.UUID = None
    produtonumerodeserie: uuid.UUID = None
