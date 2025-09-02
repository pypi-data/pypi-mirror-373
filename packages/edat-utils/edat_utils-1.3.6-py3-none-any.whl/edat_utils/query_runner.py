from sqlalchemy import create_engine
from trino.auth import BasicAuthentication
from decouple import config
from sqlalchemy.sql.expression import text

class EdatQueriyRunner:

    @staticmethod
    def unique_result(query:str, user: str):
        connection = EdatQueriyRunner.__get_connection(user)
        return connection.execute(text(query)).one()

    @staticmethod
    def list(query:str, user: str) :
        connection = EdatQueriyRunner.__get_connection(user)
        return connection.execute(text(query)).fetchall()
    
    @staticmethod
    def __get_connection(user: str):
        engine = create_engine(
            f"trino://{config('TRINO_URL')}/{config('TRINO_CATALOG')}/{config('TRINO_SCHEMA')}",
            echo=False,
            connect_args={
                "http_scheme": "https",
                "auth": BasicAuthentication(config("TRINO_USERNAME"), config("TRINO_PASSWD")),
                "extra_credential": [('a.username', user if user else config("TRINO_USERNAME"))]
            },
        )

        connection = engine.connect()
        return connection
