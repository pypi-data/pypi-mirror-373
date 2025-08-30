
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class RegraDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='regra',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    inicioadicionalnoturno: datetime.time = DTOField()
    fimadicionalnoturno: datetime.time = DTOField()
    formacompensacao: int = DTOField()
    compensaatrasocomhoraextrasabado: bool = DTOField()
    compensaatrasocomhoraextrafolga: bool = DTOField()
    compensaatrasocomhoraextradomingo: bool = DTOField()
    compensaatrasocomhoraextraferiado: bool = DTOField()
    compensafaltacomhoraextra: bool = DTOField()
    horanoturnacom_52_5_minutos: bool = DTOField()
    pagaadicionaldomingoescala: bool = DTOField()
    pagahoraextranormalsabadodomingo: bool = DTOField()
    pagahoraextrafolgarepousosabadodomingo: bool = DTOField()
    pagaadicionalferiadoescala: bool = DTOField()
    pagahoraextraferiadoescala: bool = DTOField()
    pagatolerancia: bool = DTOField()
    descontatolerancia: bool = DTOField()
    minutosiniciolimitehoraextraferiado1: int = DTOField()
    minutosiniciolimitehoraextraferiado2: int = DTOField()
    minutosiniciolimitehoraextraferiado3: int = DTOField()
    minutosiniciolimitehoraextrafolga1: int = DTOField()
    minutosiniciolimitehoraextrafolga2: int = DTOField()
    minutosiniciolimitehoraextrafolga3: int = DTOField()
    minutosiniciolimitehoraextrafolgasabado1: int = DTOField()
    minutosiniciolimitehoraextrafolgasabado2: int = DTOField()
    minutosiniciolimitehoraextrafolgasabado3: int = DTOField()
    minutosiniciolimitehoraextrafolgadomingo1: int = DTOField()
    minutosiniciolimitehoraextrafolgadomingo2: int = DTOField()
    minutosiniciolimitehoraextrafolgadomingo3: int = DTOField()
    minutosiniciolimitehoraextrasabado1: int = DTOField()
    minutosiniciolimitehoraextrasabado2: int = DTOField()
    minutosiniciolimitehoraextrasabado3: int = DTOField()
    minutosiniciolimitehoraextradomingo1: int = DTOField()
    minutosiniciolimitehoraextradomingo2: int = DTOField()
    minutosiniciolimitehoraextradomingo3: int = DTOField()
    minutosiniciolimitehoraextrasegunda1: int = DTOField()
    minutosiniciolimitehoraextrasegunda2: int = DTOField()
    minutosiniciolimitehoraextrasegunda3: int = DTOField()
    minutosiniciolimitehoraextraterca1: int = DTOField()
    minutosiniciolimitehoraextraterca2: int = DTOField()
    minutosiniciolimitehoraextraterca3: int = DTOField()
    minutosiniciolimitehoraextraquarta1: int = DTOField()
    minutosiniciolimitehoraextraquarta2: int = DTOField()
    minutosiniciolimitehoraextraquarta3: int = DTOField()
    minutosiniciolimitehoraextraquinta1: int = DTOField()
    minutosiniciolimitehoraextraquinta2: int = DTOField()
    minutosiniciolimitehoraextraquinta3: int = DTOField()
    minutosiniciolimitehoraextrasexta1: int = DTOField()
    minutosiniciolimitehoraextrasexta2: int = DTOField()
    minutosiniciolimitehoraextrasexta3: int = DTOField()
    minutostoleranciahoraextraentrada: int = DTOField()
    minutostoleranciahoraextrainiciointervalo: int = DTOField()
    minutostoleranciahoraextrafimintervalo: int = DTOField()
    minutostoleranciahoraextrasaida: int = DTOField()
    minutostoleranciahoraextrasaldointervalo: int = DTOField()
    minutostoleranciaatrasoentrada: int = DTOField()
    minutostoleranciaatrasoiniciointervalo: int = DTOField()
    minutostoleranciaatrasofimintervalo: int = DTOField()
    minutostoleranciaatrasosaida: int = DTOField()
    minutostoleranciaatrasosaldointervalo: int = DTOField()
    considerarfaltadiassemmarcacao: bool = DTOField()
    considerartolerancianoadicionalnoturno: bool = DTOField()
    compensafaltacomhoraextrasabado: bool = DTOField()
    compensafaltacomhoraextrafolga: bool = DTOField()
    compensafaltacomhoraextradomingo: bool = DTOField()
    compensafaltacomhoraextraferiado: bool = DTOField()
    gerarlancamentosdescontonopagamento: bool = DTOField()
    compensafaltacompensacaocomhoraextra: bool = DTOField()
    formabuscahorarioalternativo: int = DTOField()
    minutosiniciolimiteadicionalnoturno1: int = DTOField()
    compensahorasextrasacimalimite: bool = DTOField()
    compensafaltacompensacaocomhoraextrafolga: bool = DTOField()
    compensafaltacompensacaocomhoraextraferiado: bool = DTOField()
    compensafaltacompensacaocomhoraextrasabado: bool = DTOField()
    compensafaltacompensacaocomhoraextradomingo: bool = DTOField()
    considerartoleranciaemdiasdefolga: bool = DTOField()
    considerarsaldointervalo: bool = DTOField(
      not_null=True,)
    minutostempominimoentrejornadas: int = DTOField()
    estenderadicionalnoturnosaida: bool = DTOField()
    considerarsaldodia: bool = DTOField(
      not_null=True,)
    minutossaldodiahoraextra: int = DTOField()
    minutossaldodiaatraso: int = DTOField()

