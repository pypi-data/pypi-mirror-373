import logging
import requests

from typing import List

from edat_utils.api.models import Usuario
from edat_utils.api.custom_exceptions import (
    AccessDeniedException,
    ApiGraphiqlExeception,
    ExpiredTokenException,
)
from pydantic.type_adapter import TypeAdapter


UsuarioList = TypeAdapter(List[Usuario])

logger = logging.getLogger(__name__)


class ApiFuncionarioService:
    """Classe para gerenciar funcionarios"""

    __head_query = """
    query buscarFuncionarios {
        getDadosFuncionarios(
            filter: {"""

    __tail_query_membro = """},
            orders: {field: "nome", type: ASC},
        ) {
            items {
                identificador: matricula
                nome
                email
                telefone: ramal
                unidade
                nome_unidade: nomeUnidade
                local
                nome_local: nomeLocal
                classificacaoCarreira
                cargo: tituloCargo
                descricaoNivel
                nomeSindicato
                designacao: nomeFuncao
            }
        }
      }"""

    def __init__(self, token: str | None, url: str):
        self._base_url = url

        if not str(token).startswith("Bearer "):
            self.__DEFAULT_HEADERS = {"Authorization": f"Bearer {token}"}
        else:
            self.__DEFAULT_HEADERS = {"Authorization": token}

    def get(self, query: str) -> List[Usuario] | None:
        """Método para buscar funcionários

        :param query: string da query para pesquisa
                      Exemplo: f'in: {{matricula: {<matriculas>}}}, eq: {{ situacao: "Ativo"}}'
        :return: lista de funcionários
        """
        query = query.replace("'", '"')
        _query = f"{self.__head_query}{query}{self.__tail_query_membro}"

        response = requests.post(
            url=self._base_url,
            headers=self.__DEFAULT_HEADERS,
            json={
                "query": _query,
                "operationName": "buscarFuncionarios",
                "variables": {},
            },
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

        # print(content)

        if not content.get("data", None):
            message = "Erro ao tentar obter dados da api Funcionarios"
            logger.error(msg=f"{message}\terro={content}")
            raise ApiGraphiqlExeception(message)

        if (
            content["data"]
            and content["data"]["getDadosFuncionarios"]
            and content["data"]["getDadosFuncionarios"]["items"]
        ):
            resultado = content["data"]["getDadosFuncionarios"]["items"]
            return UsuarioList.validate_python(resultado)

        if len(content["data"]["getDadosFuncionarios"]["items"]) == 0:
            logger.warning(msg="Não foram encontrados resultados para funcionarios")
            return []
