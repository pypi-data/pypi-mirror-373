

import unittest
from nsj_integracao_api_entidades.entity_registry import EntityRegistry
from nsj_integracao_api_entidades.injector_factory import InjectorFactory
from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_rest_lib.service.service_base import ServiceBase
from nsj_rest_lib.dao.dao_base import DAOBase


from nsj_rest_lib.descriptor.dto_list_field import DTOListField


class TestListarDadosTodasEntidades(unittest.TestCase):

    def setUp(self):
        self._registry = EntityRegistry()


    def _fields_to_load(self, dto_class: DTOBase) -> dict:
        """
        Gera um dicionário com os campos a serem carregados para um DTO, incluindo os campos
        de entidades relacionadas.

        Exemplo de retorno:
        {
            "root": {"campo1", "campo2", "entidade_relacionada1", "entidade_relacionada2"},
            "entidade_relacionada1": {"campo1", "campo2"},
            "entidade_relacionada2": {"campo1", "campo2"}
        }

        Args:
            dto_class (DTOBase): Classe do DTO a ser gerado o dicionário de campos

        Returns:
            dict: Dicionário com os campos a serem carregados
        """

        fields = {}
        fields.setdefault("root", set(dto_class.fields_map.keys()))

        for _related_entity, _related_list_fields in dto_class.list_fields_map.items():
            fields["root"].add(_related_entity)
            fields.setdefault(_related_entity, set())
            _related_fields = _related_list_fields.dto_type.fields_map.keys()
            for _related_field in _related_fields:
                fields["root"].add(f"{_related_entity}.{_related_field}")
                fields[_related_entity].add(_related_field)

        return fields

    def test_listar_dados_todas_entidades(self):
        """
        Testa a listagem de dados para todas as entidades registradas, exceto 'persona.rubricasapontamento'.

        Para cada entidade registrada, instancia o DAO e o Service correspondentes,
        realiza uma consulta limitada a um registro e conta o número de entidades processadas.
        Ao final, verifica se o número de entidades carregadas corresponde ao total de entidades
        registradas menos uma (devido à exclusão da entidade específica).

        Exibe no console o total de entidades carregadas.
        """


        entities = self._registry.all_entities()

        load_count = 0

        with InjectorFactory() as injector:

            adapter = injector.db_adapter()

            for entity_name, entity in entities.items():

                # tabela só existe na web
                if entity_name == 'persona.rubricasapontamento':
                    continue

                dto = self._registry.dto_for_v3(entity_name)

                dao = DAOBase(adapter, entity)

                service = ServiceBase(
                    injector_factory=injector,
                    dao=dao,
                    dto_class=dto,
                    entity_class=entity
                )

                _fields = self._fields_to_load(dto)

                _data = service.list(
                    after=None,
                    limit=1,
                    fields=_fields,
                    order_fields=None,
                    filters=None
                )

                load_count += 1

        self.assertEqual(load_count, len(entities)-1)

        print(f"Total entities loaded: {load_count}")


    def test_mapeamento_dados_relacionados(self):
        """
        Testa se todos os campos relacionados mapeados nas entidades estão corretos.

        Este teste percorre todas as entidades registradas e verifica, para cada DTO que possui relações (list_fields_map),
        se o campo relacionado especificado realmente existe no mapeamento de campos da entidade filha (fields_map).
        Caso algum mapeamento esteja incorreto, o teste irá falhar e listar os mapeamentos errados encontrados.

        Falha se houver pelo menos um campo relacionado inexistente em alguma entidade filha.
        """

        entities = self._registry.all_entities()

        mapeamentos_errados = []

        for entity_name, entity in entities.items():

            dto_pai: DTOBase = self._registry.dto_for_v3(entity_name)

            # apenas dtos com relações importam
            if len(dto_pai.list_fields_map)==0:
                continue

            for _related_entity, _related_list_fields in dto_pai.list_fields_map.items():

                lf: DTOListField = _related_list_fields

                # checa se o campo mapeado para relação existe nos filhos
                if not lf.related_entity_field in lf.dto_type.fields_map:
                    mapeamentos_errados.append(f"{entity_name} -> {_related_entity} ({lf.related_entity_field})")


        self.assertEqual(len(mapeamentos_errados), 0, "\nMapeamentos errados:\n" + "\n".join(mapeamentos_errados))

if __name__ == "__main__":
    unittest.main()