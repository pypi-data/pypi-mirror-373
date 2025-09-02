import logging

import requests

from edat_utils.api.base import BaseApiGraphiQL
from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from edat_utils.api.models import CursoList, CursoTecnicoList


logger = logging.getLogger(__name__)


class ApiDacService(BaseApiGraphiQL):
    """Classe para buscar dados de cursos"""

    def __init__(self, url: str, token: str | None):
        super().__init__(url, token)

        self._head_query = """
        query buscarCursosDac {
            getDadosCursosDac(
                filter: {"""

        self._tail_query = """},
                orders: {field: "codigo_curso", type: ASC},
            ) {
                items {
                    dataGeracao
                    siglaOrgaoCatalogo
                    siglaOrgao
                    codigoCurso
                    nivelCurso
                    descAreaCurso
                    tipoTurnoCurso
                    classificacaoCurso
                    nomeUnidade
                    nomeUnidadeAcentuada
                    especialidadeAnuario
                    nomeCursoAnuario
                    nomeCurso
                    siglaOrgaoAnuario
                    coordenadoria
                    ultimoCatalogoVigente
                }
            }
        }"""

        self._head_query_colegios_tecnicos = """
        query buscarCursosColegiosTecnicos {
            getDadosCursosColegiosTecnicos(
                filter: {"""

        self._tail_query_colegios_tecnicos = """},
                orders: {field: "codigo_curso", type: ASC},
            ) {
                items {
                    dataGeracao
                    ultimoCatalogoVigente: ano
                    siglaOrgao: unidade
                    codigoCurso
                    nomeCurso
                    totalDeMatriculadosCurso
                    nomeUnidade: unidade
                }
            }
        }"""

    def get(self, query: str):
        """Método para buscar dados de cursos

        :return: lista de cursos
        """
        query = query.replace("'", '"')
        _query = f"{self._head_query}{query}{self._tail_query}"
        response = requests.post(
            url=self._base_url,
            headers=self._headers,
            json={"query": _query, "operationName": "buscarCursosDac", "variables": {}},
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
            message = "Erro ao tentar obter dados da api de cursos acadêmicos"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosCursosDac"]
            and content["data"]["getDadosCursosDac"]["items"]
        ):
            resultado = content["data"]["getDadosCursosDac"]["items"]
            # print(resultado)
            return CursoList.validate_python(resultado)

        if len(content["data"]["getDadosCursosDac"]["items"]) == 0:
            logger.warning(msg=f"Não foram encontrados cursos")
            return []

    def get_cursos_colegios_tecnicos(self, query: str):
        """Método para buscar dados de cursos tecnicos

        :return: lista de cursos tecnicos
        """
        query = query.replace("'", '"')
        _query = f"{self._head_query_colegios_tecnicos}{query}{self._tail_query_colegios_tecnicos}"
        response = requests.post(
            url=self._base_url,
            headers=self._headers,
            json={
                "query": _query,
                "operationName": "buscarCursosColegiosTecnicos",
                "variables": {},
            },
        )

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
            message = (
                "Erro ao tentar obter dados da api de cursos dos colégios técnicos"
            )
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosCursosColegiosTecnicos"]
            and content["data"]["getDadosCursosColegiosTecnicos"]["items"]
        ):
            resultado = content["data"]["getDadosCursosColegiosTecnicos"]["items"]
            # print(resultado)
            return CursoTecnicoList.validate_python(resultado)

        if len(content["data"]["getDadosCursosColegiosTecnicos"]["items"]) == 0:
            logger.warning(msg=f"Não foram encontrados cursos")
            return []
