from nsj_integracao_api_entidades.settings import DATABASE_HOST
from nsj_integracao_api_entidades.settings import DATABASE_PASS
from nsj_integracao_api_entidades.settings import DATABASE_PORT
from nsj_integracao_api_entidades.settings import DATABASE_NAME
from nsj_integracao_api_entidades.settings import DATABASE_USER
from nsj_integracao_api_entidades.settings import DATABASE_DRIVER

import sqlalchemy


def create_url(
    username: str,
    password: str,
    host: str,
    port: str,
    database: str,
    db_dialect: str = "postgresql+pg8000",
):
    return str(
        sqlalchemy.engine.URL.create(
            db_dialect,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )
    )


def create_pool(database_conn_url):
    # Creating database connection pool
    db_pool = sqlalchemy.create_engine(
        database_conn_url,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return db_pool


if DATABASE_DRIVER.upper() in ["SINGLE_STORE", "MYSQL"]:
    db_dialect = "mysql+pymysql"
else:
    db_dialect = "postgresql+pg8000"

database_conn_url = create_url(
    username=DATABASE_USER,
    password=DATABASE_PASS,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
    db_dialect=db_dialect,
)
db_pool = create_pool(database_conn_url)
