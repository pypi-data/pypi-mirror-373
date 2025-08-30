import unittest
from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_integracao_api_entidades.entity_registry import EntityRegistry

class TestEntityRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = EntityRegistry()

    def test_entity_for_v3(self):
        # Define test cases with input entity names and expected output classes
        test_cases = [
            ("ns.empresas", "nsj_integracao_api_entidades.entity.ns_empresas.EmpresaEntity"),
            ("persona.trabalhadores", "nsj_integracao_api_entidades.entity.persona_trabalhadores.TrabalhadoreEntity"),
            ("ponto.regras", "nsj_integracao_api_entidades.entity.ponto_regras.RegraEntity"),
        ]

        for entity_name, expected_class_path in test_cases:
            with self.subTest(entity_name=entity_name):
                entity_class = self.registry.entity_for_v3(entity_name)
                self.assertTrue(issubclass(entity_class, EntityBase))
                self.assertEqual(f"{entity_class.__module__}.{entity_class.__name__}", expected_class_path)

    def test_entity_for_v3_invalid_entity(self):

        with self.assertRaises(KeyError):
            self.registry.entity_for_v3("invalid.entity")


    def test_dto_for_v3(self):
        # Define test cases with input entity names and expected output classes
        test_cases = [
            ("ns.empresas", "nsj_integracao_api_entidades.dto.ns_empresas.EmpresaDTO"),
            ("persona.trabalhadores", "nsj_integracao_api_entidades.dto.persona_trabalhadores.TrabalhadoreDTO"),
            ("financas.bancos", "nsj_integracao_api_entidades.dto.financas_bancos.BancoDTO"),
        ]

        for dto_name, expected_class_path in test_cases:
            with self.subTest(entity_name=dto_name):
                dto_class = self.registry.dto_for_v3(dto_name)
                self.assertTrue(issubclass(dto_class, DTOBase))
                self.assertEqual(f"{dto_class.__module__}.{dto_class.__name__}", expected_class_path)

    def test_dto_for_v3_invalid_entity(self):

        with self.assertRaises(KeyError):
            self.registry.entity_for_v3("invalid.entity")




if __name__ == "__main__":
    unittest.main()