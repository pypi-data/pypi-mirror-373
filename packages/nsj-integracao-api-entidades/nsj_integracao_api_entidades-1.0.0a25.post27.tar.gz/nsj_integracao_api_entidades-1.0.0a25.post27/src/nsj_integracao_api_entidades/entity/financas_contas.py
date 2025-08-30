
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.contas",
    pk_field="conta",
    default_order_fields=["codigo"],
)
class ContaEntity(EntityBase):
    conta: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    limitenegativo: float = None
    numero: str = None
    digito: str = None
    proximocheque: str = None
    proximobordero: str = None
    bloqueado: bool = None
    acaosaldodevedor: int = None
    acaolimitenegativo: int = None
    agencianumero: str = None
    agenciadigito: str = None
    agencianome: str = None
    codigocontabil: str = None
    saldo: float = None
    limitefechamento: datetime.datetime = None
    considerasaldonofluxodecaixa: int = None
    banco: uuid.UUID = None
    tipoconta: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    codigocontabilduplicata: str = None
    usarnometitular: bool = None
    nometitular: str = None
    lastupdate: datetime.datetime = None
    compartilhaconta: bool = None
    id_grupoempresarial: uuid.UUID = None
    id_funcionario: uuid.UUID = None
    emprestimo: bool = None
    layoutpagamento: uuid.UUID = None
    chaveconciliacao: str = None
    permitirsaldonegativo: bool = None
    usarsaldominimo: bool = None
    saldominimo: float = None
    considerarsaldocheque: bool = None
    considerarsaldobordero: bool = None
    id_layoutimpressoracheque: uuid.UUID = None
    layoutcobranca: uuid.UUID = None
    id_pessoa_emprestimo: uuid.UUID = None
    id_estabelecimento_emprestimo: uuid.UUID = None
    banconumero: str = None
    tipocontaemprestimo: int = None
    nomegerente: str = None
    considerarsaldoaviso: bool = None
    possuichequeespecial: bool = None
    chequeespecial: float = None
    contapadrao: bool = None
    cpfcnpjtitular: str = None
