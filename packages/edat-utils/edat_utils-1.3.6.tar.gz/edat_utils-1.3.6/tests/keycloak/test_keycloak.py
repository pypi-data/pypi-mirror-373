import random
import string
from typing import List

from edat_utils.keycloak_service import DataKeycloakGroup, DataKeycloakUser, KeycloakService


def test_get_funcionario_username(get_keycloak_service: KeycloakService, get_usernames: List[str]):

    for username in get_usernames:
        user = get_keycloak_service.get_user_username(username)

        assert user
        assert isinstance(user, DataKeycloakUser)
        assert user.attributes
        assert user.attributes.employeeNumber


def test_get_funcionario_employeed(get_keycloak_service: KeycloakService, get_matriculas: List[int]):

    for matricula in get_matriculas:
        user = get_keycloak_service.get_user_employeeNumber(matricula)

        assert user
        assert isinstance(user, DataKeycloakUser)
        assert user.attributes
        assert user.attributes.employeeNumber


def test_get_roles(get_keycloak_service: KeycloakService):
    roles = get_keycloak_service.get_roles()

    assert len(roles) > 0


def test_get_groups(get_keycloak_service: KeycloakService):
    groups = get_keycloak_service.get_groups()

    assert len(groups) > 0

    for group in groups:
        assert isinstance(group, DataKeycloakGroup)


def test_crud_group(get_keycloak_service: KeycloakService):
    letters = string.ascii_lowercase
    name = str(''.join(random.choice(letters) for _ in range(10))).upper()

    get_keycloak_service.create_group(name=name)

    group = get_keycloak_service.get_group_by_path(path=name)

    assert group
    assert isinstance(group, DataKeycloakGroup)

    deleted= get_keycloak_service.delete_group(group.id)
    group = get_keycloak_service.get_group_by_path(path=name)

    assert deleted
    assert not group


