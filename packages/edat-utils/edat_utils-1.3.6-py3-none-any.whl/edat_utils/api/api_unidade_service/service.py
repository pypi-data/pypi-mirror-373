import logging
from typing import List

import requests

from edat_utils.api.base import BaseApiGraphiQL
from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from edat_utils.api.models import UnidadeSchema, UnidadeSchemaList


logger = logging.getLogger(__name__)


class ApiUnidadeService(BaseApiGraphiQL):
    """Classe para gerenciar unidades"""

    def __init__(self, url: str, token: str | None) -> None:
        super().__init__(url=url, token=token)
        self._head_query = """
        query buscarUnidades {
            getDadosUnidades(
                filter: {"""

        self._tail_query = """},
                orders: {field: "numero_lotacao", type: ASC},
            ) {
                items {
                    numeroLotacao
                    lotacao
                    unidade
                    nomeUnidade
                    nomeUnidadeAcentuada
                    tipoUnidade
                    categoriaUnidade
                    siglaArea
                    descricaoArea
                }
            }
        }"""

    def get(self, query: str):
        """Método para buscar unidades de acordo com a categoria

        :param query: query graphiql
        :return: lista de objetos do tipo UnidadeSchema
        """
        query = f"{query}".replace("'", '"')
        _query = f"{self._head_query}{query}{self._tail_query}"
        response = requests.post(
            url=self._base_url,
            headers=self._headers,
            json={"query": _query, "operationName": "buscarUnidades", "variables": {}},
        )

        if response.status_code == 500:
            content = response.text
            message = "Erro inesperado"
            logger.exception(msg=f"{message}\terror={content}")
            raise ApiGraphiqlExeception(message)

        if response.status_code == 400:
            message = "Erro na requisição"
            logger.error(msg=f"{message}\terror={response.text}")
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
            message = "Erro ao tentar obter dados da api RH unidades"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosUnidades"]
            and content["data"]["getDadosUnidades"]["items"]
        ):
            resultado = content["data"]["getDadosUnidades"]["items"]
            # print(resultado)
            return UnidadeSchemaList.validate_python(resultado)

        if len(content["data"]["getDadosUnidades"]["items"]) == 0:
            logger.warning(msg=f"Não foram encontrados resultados para as unidades")
            return []
