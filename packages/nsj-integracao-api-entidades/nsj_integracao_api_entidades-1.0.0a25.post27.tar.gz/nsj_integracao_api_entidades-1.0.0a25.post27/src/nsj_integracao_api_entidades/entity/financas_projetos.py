
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.projetos",
    pk_field="projeto",
    default_order_fields=["codigo"],
)
class ProjetoEntity(EntityBase):
    projeto: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    finalizado: bool = None
    datainicio: datetime.datetime = None
    datafim: datetime.datetime = None
    grupoempresarial: uuid.UUID = None
    lastupdate: datetime.datetime = None
    cliente_id: uuid.UUID = None
    importacao_hash: str = None
    estabelecimento_id: uuid.UUID = None
    tipoprojeto_id: uuid.UUID = None
    observacao: str = None
    situacao: int = None
    data_criacao: datetime.datetime = None
    criado_por: uuid.UUID = None
    updated_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
    valor: float = None
    documentovinculado: uuid.UUID = None
    origem: str = None
    tipodocumentovinculado: int = None
    sincronizaescopo: bool = None
    localdeuso: uuid.UUID = None
    sincronizasolicitacao: bool = None
    pcp: bool = None
    dataentrega: datetime.datetime = None
    tipoprojeto: uuid.UUID = None
    tempoadquirido: int = None
    responsavel: uuid.UUID = None
    tempoprevisto: int = None
    projetopai: uuid.UUID = None
    codigopai: str = None
    usuario_responsavel: uuid.UUID = None
    anotacao: str = None
    producao_processo: uuid.UUID = None
    producao_modelo_processo: uuid.UUID = None
    created_at: datetime.datetime = None
    responsavel_conta_nasajon: dict = None
    endereco_id: uuid.UUID = None
    localdeestoque_id: uuid.UUID = None
    projeto_adm_debito: bool = None
    bloqueado: bool = None
