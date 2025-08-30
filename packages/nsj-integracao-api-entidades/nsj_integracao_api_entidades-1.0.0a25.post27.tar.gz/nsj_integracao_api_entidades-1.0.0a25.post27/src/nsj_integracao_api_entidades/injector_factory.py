from sqlalchemy.engine.base import Connection


class InjectorFactory:
    _db_connection: Connection

    def __enter__(self):
        from nsj_integracao_api_entidades.db_pool_config import db_pool
        self._db_connection = db_pool.connect()
        self._db_connection.execute("select set_config('symmetric.triggers_disabled', '1', false);")
        self._db_connection.execute("SET TIME ZONE 'America/Sao_Paulo'")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db_connection.close()

    def db_adapter(self):
        from nsj_gcf_utils.db_adapter2 import DBAdapter2
        return DBAdapter2(self._db_connection)