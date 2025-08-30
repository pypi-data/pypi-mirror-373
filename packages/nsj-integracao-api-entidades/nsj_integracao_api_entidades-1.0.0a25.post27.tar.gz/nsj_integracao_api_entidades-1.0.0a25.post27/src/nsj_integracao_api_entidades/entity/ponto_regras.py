
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ponto.regras",
    pk_field="regra",
    default_order_fields=["codigo"],
)
class RegraEntity(EntityBase):
    regra: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    inicioadicionalnoturno: datetime.time = None
    fimadicionalnoturno: datetime.time = None
    formacompensacao: int = None
    compensaatrasocomhoraextrasabado: bool = None
    compensaatrasocomhoraextrafolga: bool = None
    compensaatrasocomhoraextradomingo: bool = None
    compensaatrasocomhoraextraferiado: bool = None
    compensafaltacomhoraextra: bool = None
    horanoturnacom_52_5_minutos: bool = None
    pagaadicionaldomingoescala: bool = None
    pagahoraextranormalsabadodomingo: bool = None
    pagahoraextrafolgarepousosabadodomingo: bool = None
    pagaadicionalferiadoescala: bool = None
    pagahoraextraferiadoescala: bool = None
    pagatolerancia: bool = None
    descontatolerancia: bool = None
    minutosiniciolimitehoraextraferiado1: int = None
    minutosiniciolimitehoraextraferiado2: int = None
    minutosiniciolimitehoraextraferiado3: int = None
    minutosiniciolimitehoraextrafolga1: int = None
    minutosiniciolimitehoraextrafolga2: int = None
    minutosiniciolimitehoraextrafolga3: int = None
    minutosiniciolimitehoraextrafolgasabado1: int = None
    minutosiniciolimitehoraextrafolgasabado2: int = None
    minutosiniciolimitehoraextrafolgasabado3: int = None
    minutosiniciolimitehoraextrafolgadomingo1: int = None
    minutosiniciolimitehoraextrafolgadomingo2: int = None
    minutosiniciolimitehoraextrafolgadomingo3: int = None
    minutosiniciolimitehoraextrasabado1: int = None
    minutosiniciolimitehoraextrasabado2: int = None
    minutosiniciolimitehoraextrasabado3: int = None
    minutosiniciolimitehoraextradomingo1: int = None
    minutosiniciolimitehoraextradomingo2: int = None
    minutosiniciolimitehoraextradomingo3: int = None
    minutosiniciolimitehoraextrasegunda1: int = None
    minutosiniciolimitehoraextrasegunda2: int = None
    minutosiniciolimitehoraextrasegunda3: int = None
    minutosiniciolimitehoraextraterca1: int = None
    minutosiniciolimitehoraextraterca2: int = None
    minutosiniciolimitehoraextraterca3: int = None
    minutosiniciolimitehoraextraquarta1: int = None
    minutosiniciolimitehoraextraquarta2: int = None
    minutosiniciolimitehoraextraquarta3: int = None
    minutosiniciolimitehoraextraquinta1: int = None
    minutosiniciolimitehoraextraquinta2: int = None
    minutosiniciolimitehoraextraquinta3: int = None
    minutosiniciolimitehoraextrasexta1: int = None
    minutosiniciolimitehoraextrasexta2: int = None
    minutosiniciolimitehoraextrasexta3: int = None
    minutostoleranciahoraextraentrada: int = None
    minutostoleranciahoraextrainiciointervalo: int = None
    minutostoleranciahoraextrafimintervalo: int = None
    minutostoleranciahoraextrasaida: int = None
    minutostoleranciahoraextrasaldointervalo: int = None
    minutostoleranciaatrasoentrada: int = None
    minutostoleranciaatrasoiniciointervalo: int = None
    minutostoleranciaatrasofimintervalo: int = None
    minutostoleranciaatrasosaida: int = None
    minutostoleranciaatrasosaldointervalo: int = None
    considerarfaltadiassemmarcacao: bool = None
    considerartolerancianoadicionalnoturno: bool = None
    compensafaltacomhoraextrasabado: bool = None
    compensafaltacomhoraextrafolga: bool = None
    compensafaltacomhoraextradomingo: bool = None
    compensafaltacomhoraextraferiado: bool = None
    gerarlancamentosdescontonopagamento: bool = None
    compensafaltacompensacaocomhoraextra: bool = None
    formabuscahorarioalternativo: int = None
    minutosiniciolimiteadicionalnoturno1: int = None
    compensahorasextrasacimalimite: bool = None
    compensafaltacompensacaocomhoraextrafolga: bool = None
    compensafaltacompensacaocomhoraextraferiado: bool = None
    compensafaltacompensacaocomhoraextrasabado: bool = None
    compensafaltacompensacaocomhoraextradomingo: bool = None
    considerartoleranciaemdiasdefolga: bool = None
    considerarsaldointervalo: bool = None
    minutostempominimoentrejornadas: int = None
    estenderadicionalnoturnosaida: bool = None
    considerarsaldodia: bool = None
    minutossaldodiahoraextra: int = None
    minutossaldodiaatraso: int = None
