# pylint: disable=W0611


from nsj_integracao_api_entidades.entity_registry import EntityRegistry
_reg = EntityRegistry()
a = _reg.entity_for('ns.empresas')
b = _reg.dto_for('persona.trabalhadores')