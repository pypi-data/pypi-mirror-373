import logging
from typing import List

import requests

from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from edat_utils.api.models import Usuario, UsuarioList


logger = logging.getLogger(__name__)


class ApiAcademicoService:
    """Classe para buscar alunos"""

    __head_query = """
    query buscarAlunos {
        getDadosAlunos(
            filter: {"""

    __tail_query = """},
            orders: {field: "nomeCivilAluno", type: ASC},
        ) {
            items {
                identificador: ra
                nome: nomeCivilAluno
                email: emailInstitucional
                unidade
                nome_unidade: nomeUnidade
                local: unidade
                nomeLocal: nomeUnidade
                telefone: ra
                cargo: nomeCurso
            }
        }
      }"""

    def __init__(self, token: str | None, url: str):
        self._base_url = url

        if not str(token).startswith("Bearer "):
            self.__DEFAULT_HEADERS = {"Authorization": f"Bearer {token}"}
        else:
            self.__DEFAULT_HEADERS = {"Authorization": token}

    def get(self, query: str) -> List[Usuario]:
        """Método para buscar alunos

        :param query: string da query do graphql
        :return: lista de DataAcademicoAluno
        """
        query = query.replace("'", '"')
        _query = f"{self.__head_query}{query}{self.__tail_query}".strip()
        response = requests.post(
            url=self._base_url,
            headers=self.__DEFAULT_HEADERS,
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

        if not content.get("data", None):
            message = "Erro ao tentar obter dados da api Academico"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosAlunos"]
            and content["data"]["getDadosAlunos"]["items"]
        ):
            resultado = content["data"]["getDadosAlunos"]["items"]
            alunos_unicos = {}

            # Filtrar alunos duplicados
            for aluno in resultado:
                if aluno["identificador"] not in alunos_unicos:
                    alunos_unicos[aluno["identificador"]] = aluno

            return UsuarioList.validate_python(list(alunos_unicos.values()))

        if len(content["data"]["getDadosAlunos"]["items"]) == 0:
            logger.warning(msg="Não foram encontrados resultados para alunos")
            return []
