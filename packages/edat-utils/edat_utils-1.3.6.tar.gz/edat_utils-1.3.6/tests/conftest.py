import logging
import ast
import os
from typing import Generator

from dotenv import load_dotenv
import pytest
import requests

from edat_utils.api import ApiAcademicoService, ApiFuncionarioService
from edat_utils.api.api_colegios_service.service import ApiColegiosTecnicosService
from edat_utils.api.api_dac_service.service import ApiDacService
from edat_utils.api.api_lotacao_service.service import ApiLotacaoService
from edat_utils.api.api_unidade_service.service import ApiUnidadeService
from edat_utils.api.usuario_service import UsuarioService
from edat_utils.edat_keycloak_service import EdatKeycloakService
from edat_utils.keycloak_service import KeycloakService


logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente
load_dotenv()

# variáveis de ambiente
rh_private_url = os.getenv("RH_PRIVATE_URL", "")
rh_public_url = os.getenv("RH_PUBLIC_URL", "")
academico_private_url = os.getenv("ACADEMICO_PRIVATE_URL", "")
academico_public_url = os.getenv('ACADEMICO_"PUBLIC_URL', "")
keycloak_url = os.getenv("KEYCLOAK_URL", "")

auth_url = os.getenv("AUTH_URL", "")
client_id = os.getenv("CLIENT_ID", "")
client_scope = os.getenv("CLIENT_SCOPE", "")
username = os.getenv("USERNAME", "")
password = os.getenv("PASSWORD", "")

a_client_id = os.getenv("A_CLIENT_ID", "")
a_client_secret = os.getenv("A_CLIENT_SECRET", "")
a_client_scope = os.getenv("A_CLIENT_SCOPE", "")
a_grant_type = os.getenv("A_GRANT_TYPE", "")

usernames = os.getenv("USERNAMES", "[]")
matriculas = os.getenv("MATRICULAS", "[]")
identificadores = os.getenv("IDENTIFICADORES", "[]")


@pytest.fixture(scope="session")
def get_token() -> Generator:
    access_token = None

    data = {
        "client_id": client_id,
        "client_secret": client_scope,
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    response = requests.post(auth_url, data=data)

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info["access_token"]
    else:
        logger.error(
            msg=f"Erro ao obter o token: {response.status_code} {response.text}"
        )

    yield access_token


@pytest.fixture()
def get_api_funcionario_service(get_token: str) -> Generator:
    yield ApiFuncionarioService(token=get_token, url=rh_private_url)


@pytest.fixture()
def get_api_academico_service(get_token: str) -> Generator:
    yield ApiAcademicoService(token=get_token, url=academico_private_url)


@pytest.fixture()
def get_api_colegios_tecnicos_service(get_token: str) -> Generator:
    yield ApiColegiosTecnicosService(token=get_token, url=academico_private_url)


@pytest.fixture()
def get_api_unidade_service(get_token: str) -> Generator:
    yield ApiUnidadeService(token=get_token, url=rh_public_url)


@pytest.fixture()
def get_api_lotacao_service(get_token: str) -> Generator:
    yield ApiLotacaoService(token=get_token, url=rh_public_url)


@pytest.fixture()
def get_api_dac_service(get_token: str) -> Generator:
    yield ApiDacService(token=get_token, url=academico_private_url)


@pytest.fixture()
def get_keycloak_service() -> Generator:
    yield KeycloakService(
        base_url=keycloak_url, username=username, password=password, realm="test"
    )


@pytest.fixture()
def get_usuario_service(
    get_api_funcionario_service,
    get_api_academico_service,
    get_api_colegios_tecnicos_service,
) -> Generator:
    yield UsuarioService(
        funcionario_service=get_api_funcionario_service,
        academico_service=get_api_academico_service,
        colegio_service=get_api_colegios_tecnicos_service,
    )


@pytest.fixture()
def get_edat_keycloak_service() -> Generator:
    yield EdatKeycloakService(
        base_url=keycloak_url,
        client_id=a_client_id,
        client_secret=a_client_secret,
        realm="test",
    )


@pytest.fixture
def get_usernames() -> Generator:
    yield ast.literal_eval(usernames)


@pytest.fixture
def get_identificadores() -> Generator:
    yield ast.literal_eval(identificadores)


@pytest.fixture
def get_matriculas() -> Generator:
    yield ast.literal_eval(matriculas)
