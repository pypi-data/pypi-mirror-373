import logging
from typing import List
import requests

from edat_utils.api.base import BaseApiGraphiQL
from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from edat_utils.api.models import Usuario, UsuarioList


logger = logging.getLogger(__name__)


class ApiColegiosTecnicosService(BaseApiGraphiQL):
    """Classe para buscar alunos de colégios técnicos"""

    def __init__(self, token: str, url: str) -> None:
        super().__init__(token=token, url=url)

        self._head_query = """
        query buscarAlunos {
            getDadosAlunosColegiosTecnicos(
                filter: {"""

        self._tail_query = """},
                orders: {field: "nome_aluno", type: ASC},
            ) {
                items {
                    identificador: ra
                    nome: nomeAluno
                    email: ra
                    unidade
                    telefone: ra
                    cargo: nomeCurso
                    nomeCurso
                }
            }
        }"""

    def get(self, query: str) -> List[Usuario]:
        """Método para buscar alunos de colégios tecnicos

        :param query: string da query do graphql
        :return: lista de usuario
        """
        query = query.replace("'", '"')
        _query = f"{self._head_query}{query}{self._tail_query}"
        response = requests.post(
            url=self._base_url,
            headers=self._headers,
            json={"query": _query, "operationName": "buscarAlunos", "variables": {}},
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
        usuarios = []

        if not content.get("data", None):
            message = "Erro ao tentar obter dados da api Academico"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosAlunosColegiosTecnicos"]
            and content["data"]["getDadosAlunosColegiosTecnicos"]["items"]
        ):
            resultado = content["data"]["getDadosAlunosColegiosTecnicos"]["items"]
            return UsuarioList.validate_python(resultado)

        if len(content["data"]["getDadosAlunosColegiosTecnicos"]["items"]) == 0:
            logger.warning(
                msg="Não foram encontrados resultados para alunos de colégios tecnicos"
            )

        return usuarios
