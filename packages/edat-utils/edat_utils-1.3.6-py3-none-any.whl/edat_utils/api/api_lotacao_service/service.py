import logging

import requests

from edat_utils.api.base import BaseApiGraphiQL
from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from edat_utils.api.models import UnidadeSchemaList


logger = logging.getLogger(__name__)


class ApiLotacaoService(BaseApiGraphiQL):
    """Classe para gerenciar unidades"""

    def __init__(self, url: str, token: str | None):
        super().__init__(url, token)

        self._head_query = """
        query buscarLotacoes {
            getDadosLotacoes(
                filter: {"""

        self._tail_query = """},
                orders: {field: "unidade", type: ASC},
            ) {
                items {
                    unidade
                    numeroUnidade
                    numeroLocal
                    codigoUnidade
                    unidadeOriginal
                    nomeUnidade
                    nomeUnidadeAcentuada
                    categoriaUnidade
                    local
                    nomeLocal
                    codigoLocal
                    siglaArea
                    tipoUnidade
                }
            }
        }"""

    def get(self, query: str):
        """Método para buscar lotacoes

        :param query: query graphiql
        :return: lista de api rh unidade
        """
        query = f"{query}".replace("'", '"')
        _query = f"{self._head_query}{query}{self._tail_query}"

        response = requests.post(
            url=self._base_url,
            headers=self._headers,
            json={"query": _query, "operationName": "buscarLotacoes", "variables": {}},
        )

        if response.status_code == 500:
            content = response.text
            message = "Erro inesperado"
            logger.exception(msg=f"{message}\terror={content}")
            raise ApiGraphiqlExeception(message)

        if response.status_code == 401:
            content = response.json()
            if content["message"] == "Bad token; invalid JSON":
                message = "Token mal formatado"
                logger.error(msg=f"{message}\terror={content}")
                raise AccessDeniedException(message=message)
            else:
                message = (
                    "Token expirado"
                    if content["message"] != "Token issuer not allowed"
                    else "O orgão emissor do token não é reconhecido."
                )
                logger.error(msg=f"{message}\terror={content}")
                raise ExpiredTokenException(message)

        if response.status_code == 403:
            message = "Acesso Negado"
            logger.error(msg=f"{message}\terror={response.json()}")
            raise AccessDeniedException(message)

        content = response.json()

        if not content.get("data", None):
            message = "Erro ao tentar obter dados da api de lotações"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        # Se não existir dados no retorno da api
        if len(content["data"]["getDadosLotacoes"]["items"]) == 0:
            logger.warning(msg=f"Não foram encontrados resultados para as lotacoes")
            return []

        # Havendo dados, formata a resposta para retorno
        if (
            content["data"]
            and content["data"]["getDadosLotacoes"]
            and content["data"]["getDadosLotacoes"]["items"]
        ):
            result = content["data"]["getDadosLotacoes"]["items"]
            return UnidadeSchemaList.validate_python(result)
