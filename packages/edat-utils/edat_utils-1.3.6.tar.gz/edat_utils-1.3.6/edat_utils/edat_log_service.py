from datetime import datetime
import logging

from sqlalchemy import MetaData, Table, create_engine, insert
from sqlalchemy.pool import NullPool


logger = logging.getLogger(__name__)


class EdatLogService:
    """ Serviço de persistência de logs
    """

    def __init__(
            self,
            url: str,
            nome_tabela: str,
            schema: str = 'public'  # Adicionando o parâmetro schema com valor padrão 'public'
        ) -> None:
        """ Construtor da classe

            :param nome_tabela: nome da tabela alvo onde será inserido os logs
            "param url: url de conexão
            :param schema: Nome do schema no banco de dados.
        """
        try:
            metadata = MetaData()

            # ver mais em https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing
            self.__engine = create_engine(
                url=url, poolclass=NullPool
            )
            self.__tabela = Table(
                nome_tabela, metadata, autoload_with=self.__engine, extend_existing=True, schema=schema
            )

            logger.debug(msg=f'Conectado ao banco de dados de log')

        except Exception as e:
            logger.error(msg=f'Erro ao conectar no banco de dados: {str(e)}')
            raise Exception(e)

    def __converter_datetime_para_str(self, params):
        """ Método privado para converter dados do tipo datetime/timestamp
            em string para serialização no campo tipo JSON do postgresql

            :param params: parâmetros nomeados para serem convertidos
        """
        converted_params = {}

        for key, value in params.items():
            if isinstance(value, (datetime,)):
                converted_params[key] = str(value)
            elif isinstance(value, dict):
                converted_params[key] = self.__converter_datetime_para_str(value)
            elif isinstance(value, (list, tuple)):
                converted_params[key] = [self.__converter_datetime_para_str(item) if isinstance(item, dict) else item for item in value]
            else:
                converted_params[key] = value

        return converted_params

    def salvar(self, **kwargs) -> None:
        """
            Método para persistir em tabela informações relevantes sobre o evento realizado pelo usuário.

            :param kwargs: campos nomeados para inserir na tabela correspondente.
        """
        try:
            converted_kwargs = self.__converter_datetime_para_str(kwargs)
            stmt = insert(self.__tabela).values(converted_kwargs)
            logger.debug(msg=f'Inserindo registro no banco de dados de log: {stmt}')

            self.__engine.dispose()
            with self.__engine.connect() as conn:
                conn.execute(stmt)
                conn.commit()

        except Exception as e:
            logger.error(msg=f'Erro ao salvar na tabela {self.__tabela} de logs: {str(e)}')
            raise Exception(e)
