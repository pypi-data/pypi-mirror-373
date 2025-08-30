import copy

import hashlib
import datetime

from typing import Callable
from zoneinfo import ZoneInfo
from enum import Enum
from flask import request

from nsj_rest_lib.controller.controller_util import DEFAULT_RESP_HEADERS
from nsj_rest_lib.controller.route_base import RouteBase
from nsj_rest_lib.dto.dto_base import DTOBase, DTOFieldFilter
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_list_field import DTOListField
from nsj_rest_lib.descriptor.filter_operator import FilterOperator
from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.exception import MissingParameterException
from nsj_rest_lib.injector_factory_base import NsjInjectorFactoryBase
from nsj_rest_lib.settings import get_logger, DEFAULT_PAGE_SIZE

from nsj_gcf_utils.json_util import json_dumps, json_loads
from nsj_gcf_utils.pagination_util import PaginationException
from nsj_gcf_utils.rest_error_util import format_json_error

from nsj_integracao_api_entidades.nsj_rest_lib_extensions.dao.integridade_dao import IntegridadeDAO
from nsj_integracao_api_entidades.nsj_rest_lib_extensions.service.integridade_service\
    import IntegridadeService


class TipoVerificacaoIntegridade(Enum):
    CONTAGEM = "CONTAGEM"     # Compara número de registros entre web e desktop
    IDENTIFICADOR = "ID"      # Compara chaves, identifica registros a criar/excluir
    HASH = "HASH"             # Compara chave + hash, identifica criar/atualizar/excluir
    ATRIBUTO = "ATRIBUTO"     # Como HASH mas detalha campos com diferença


class IntegrityCheckRoute(RouteBase):

    # Campos não elegíveis para comparação de integridade
    _ignored_fields = ["tenant", "lastupdate"]

    _tz_br: ZoneInfo
    #_tz_br = ZoneInfo("UTC-03:00").

    def __init__(
        self,
        url: str,
        http_method: str,
        dto_class: DTOBase,
        entity_class: EntityBase,
        injector_factory: NsjInjectorFactoryBase = NsjInjectorFactoryBase,
        service_name: str = None,
        handle_exception: Callable = None,
    ):
        super().__init__(
            url=url,
            http_method=http_method,
            dto_class=dto_class,
            entity_class=entity_class,
            dto_response_class=None,
            injector_factory=injector_factory,
            service_name=service_name,
            handle_exception=handle_exception,
        )
        self._tz_br = ZoneInfo("America/Sao_Paulo")


    def _get_service(self, factory: NsjInjectorFactoryBase, args) -> IntegridadeService:
        """
        Return service instance, by service name or using NsjServiceBase.
        """

        if self._service_name is not None:
            _service = factory.get_service_by_name(self._service_name)
        else:
            _service = IntegridadeService(
                factory,
                IntegridadeDAO(factory.db_adapter(), self._entity_class),
                self._dto_class,
                self._entity_class,
                self._dto_response_class,
            )

        if not args.get("custom_filter"):
            return _service

        _custom_filter = json_loads(args.get("custom_filter"))
        if isinstance(_custom_filter, list):
            for _filtro in _custom_filter:
                if "campo" in _filtro and "valor" in _filtro and "operador" in _filtro:
                    _alias = f"{_filtro['campo']}_{_filtro['operador']}"
                    _operator = (
                        getattr(FilterOperator, _filtro['operador'].upper(), FilterOperator.EQUALS)
                    )
                    _filter = DTOFieldFilter(_alias, _operator)
                    _filter.set_field_name(_filtro['campo'])
                    _service._dto_class.field_filters_map[_alias] = _filter
                else:
                    ValueError(f"O filtro extra deve conter campo,valor e operador': {_filtro} fornecido.")
        else:
            raise ValueError("filtros extras devem ser uma lista")


        return _service

    def integrity_fields(self, dto) -> dict:
        fields = {"root": set()}

        for _field_name in sorted(dto.integrity_check_fields_map.keys()):

            if _field_name in self._ignored_fields:
                continue

            _field_obj = dto.integrity_check_fields_map[_field_name]

            if isinstance(_field_obj, DTOField):
                fields["root"].add(_field_name)
                continue

            if isinstance(_field_obj, DTOListField):
                fields["root"].add(_field_name)
                fields.setdefault(_field_name, set())

                for _related_field in sorted(_field_obj.dto_type.integrity_check_fields_map.keys()):
                    if not _related_field in self._ignored_fields:
                        fields["root"].add(f"{_field_name}.{_related_field}")
                        fields[_field_name].add(_related_field)

        return fields

    def tratar_campos_comparacao(self, dados: dict, campos_ignorados: list):

        keys_to_delete = []
        for chave, valor in dados.items():

            # Remove timezone para comparação
            if isinstance(valor, (datetime.datetime, datetime.date)):
                if valor.tzinfo is not None and valor.tzinfo != self._tz_br:
                    dados[chave] = valor.astimezone(self._tz_br).replace(microsecond=0, tzinfo=None)
                else:
                    dados[chave] = valor.replace(microsecond=0, tzinfo=None)

            # Ignora campos não úteis
            if chave in campos_ignorados:
                keys_to_delete.append(chave)

            # Aplica regras em sublistas
            if isinstance(valor, list):
                valor.sort(key=lambda x: x['id'])
                for item in valor:
                    self.tratar_campos_comparacao(item, campos_ignorados)

        for chave in keys_to_delete:
            del dados[chave]


    def convert_to_field_hash(self, dto, integrity_fields, source : bool):
        data = dto.convert_to_dict(integrity_fields)

        self.tratar_campos_comparacao(data, self._ignored_fields)

        concatenated_values = json_dumps(data)

        result = {
            "id": str(data[self._dto_class.pk_field]),
            "hash": hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()
        }
        if source:
            result["_source"] = concatenated_values
        return result

    def handle_request(self):
        """
        Tratando requisições HTTP Get (para capturar os dados de integridade).
        """

        with self._injector_factory() as factory:
            try:
                # Recuperando os parâmetros básicos
                args = request.args
                limit = int(args.get("limit", DEFAULT_PAGE_SIZE))
                current_after = args.get("after") or args.get("offset")
                source = args.get('source', False, type=lambda value: value.lower() == 'true')

                tipo = TipoVerificacaoIntegridade(args.get("type")) if args.get("type") else TipoVerificacaoIntegridade.HASH

                if tipo == TipoVerificacaoIntegridade.HASH:

                    # Tratando dos fields
                    fields = {}
                    fields["root"] = set(self._dto_class.fields_map.keys())

                    for _related_entity, _related_list_fields in self._dto_class.list_fields_map.items():
                        fields["root"].add(_related_entity)
                        fields.setdefault(_related_entity, set())
                        _related_fields = _related_list_fields.dto_type.fields_map.keys()
                        for _related_field in _related_fields:
                            fields["root"].add(f"{_related_entity}.{_related_field}")
                            fields[_related_entity].add(_related_field)

                    # Tratando dos filters e search_query
                    filters = {}
                    search_query = None
                    for arg in args:
                        if arg.lower() == "search":
                            search_query = args.get(arg)
                            continue

                        if arg in ["limit", "after", "offset", "fields"]:
                            continue

                        if arg in self._dto_class.partition_fields:
                            continue

                        filters[arg] = args.get(arg)

                    # Tratando campos de particionamento
                    for field in self._dto_class.partition_fields:
                        value = args.get(field)
                        if value is None:
                            raise MissingParameterException(field)

                        filters[field] = value

                    # Construindo os objetos
                    service = self._get_service(factory, args)

                    # Quantidade de dados
                    _count = 0
                    _integrity_fields = self.integrity_fields(self._dto_class)
                    _dict_data = []

                    # Chamando o service (método list)
                    _data = service.list(
                        current_after,
                        limit,
                        fields,
                        None,
                        filters,
                        search_query=search_query,
                    )

                    _count = _count + len(_data)

                    # Convertendo para o formato de dicionário (permitindo omitir campos do DTO)
                    _cp_fields = copy.deepcopy(_integrity_fields)
                    while _data:
                        dto = _data.pop(0)
                        _dict_data.append(self.convert_to_field_hash(dto, _cp_fields, source))

                    # Construindo o corpo da página
                    resp = {
                        'registros' : _count,
                        'campos': {
                            "_": ",".join(sorted(_integrity_fields['root'])),
                        },
                        'dados': _dict_data
                    }

                elif tipo == TipoVerificacaoIntegridade.IDENTIFICADOR:

                    # Tratando dos fields
                    fields = {}
                    fields["root"] = set(self._dto_class.fields_map.keys())

                    # Tratando dos filters e search_query
                    filters = {}
                    search_query = None
                    for arg in args:
                        if arg.lower() == "search":
                            search_query = args.get(arg)
                            continue

                        if arg in ["limit", "after", "offset", "fields"]:
                            continue

                        if arg in self._dto_class.partition_fields:
                            continue

                        filters[arg] = args.get(arg)

                    # Tratando campos de particionamento
                    for field in self._dto_class.partition_fields:
                        value = args.get(field)
                        if value is None:
                            raise MissingParameterException(field)

                        filters[field] = value

                    # Construindo os objetos
                    service = self._get_service(factory, args)

                    # Quantidade de dados
                    _count = 0

                    _data = service.list_ids_integridade(
                        after=current_after,
                        limit=limit,
                        order_fields=None,
                        filters=filters,
                    )

                    _count = _count + len(_data)

                    # Construindo o corpo da página
                    resp = {
                        'registros' : _count,
                        'campos': {
                            "_": self._dto_class.pk_field,
                        },
                        'dados': _data
                    }
                else:
                    raise NotImplementedError(f"Tipo de integridade {tipo} ainda nao implementado")

                # Retornando a resposta da requuisição
                return (json_dumps(resp), 200, {**DEFAULT_RESP_HEADERS})
            except MissingParameterException as e:
                get_logger().warning(e)
                if self._handle_exception is not None:
                    return self._handle_exception(e)
                else:
                    return (format_json_error(e), 400, {**DEFAULT_RESP_HEADERS})
            except PaginationException as e:
                get_logger().warning(e)
                if self._handle_exception is not None:
                    return self._handle_exception(e)
                else:
                    return (format_json_error(e), 400, {**DEFAULT_RESP_HEADERS})
            except Exception as e:
                get_logger().exception(e)
                if self._handle_exception is not None:
                    return self._handle_exception(e)
                else:
                    return (
                        format_json_error(f"Erro desconhecido: {e}"),
                        500,
                        {**DEFAULT_RESP_HEADERS},
                    )
