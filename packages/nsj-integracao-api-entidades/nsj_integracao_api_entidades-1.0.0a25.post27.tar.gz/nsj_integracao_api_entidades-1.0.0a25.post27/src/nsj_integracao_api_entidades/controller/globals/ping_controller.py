from nsj_integracao_api_entidades.controller.controller_util import DEFAULT_RESP_HEADERS
from nsj_integracao_api_entidades.settings import application, APP_NAME
from nsj_gcf_utils.json_util import json_dumps

GET_ROUTE = f'/{APP_NAME}/ping'


@application.route(GET_ROUTE, methods=['GET'])
def get_ping():
    return (json_dumps({"msg": "Pong!"}), 200, {**DEFAULT_RESP_HEADERS})
