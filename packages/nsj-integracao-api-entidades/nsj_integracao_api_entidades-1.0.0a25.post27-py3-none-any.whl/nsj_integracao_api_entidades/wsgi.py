import pkgutil
import importlib

# Importando arquivos de configuração
from nsj_integracao_api_entidades.settings import (
    application, APP_NAME, MOPE_CODE, DATABASE_HOST, DATABASE_NAME
)

from nsj_integracao_api_entidades import controller

print(f' App name: {APP_NAME}', f' MOPE_CODE: {MOPE_CODE}')

for _, name, _ in pkgutil.iter_modules(controller.__path__):
    print(f'Importando controller: {name}')
    importlib.import_module(f'nsj_integracao_api_entidades.controller.{name}')

print(f"DB server: {DATABASE_HOST}:{DATABASE_NAME}")

# print('Rotas registradas:')
# for rule in application.url_map.iter_rules():
#     print(f'{rule.endpoint}: {rule}')

if __name__ == '__main__':
    application.run(port=5000)


