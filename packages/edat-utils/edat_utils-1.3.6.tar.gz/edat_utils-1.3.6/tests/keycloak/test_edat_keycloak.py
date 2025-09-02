import random
import string
from typing import List

from edat_utils.edat_keycloak_service import CreateRealmRole, DataKeycloakGroup, DataKeycloakUser, EdatKeycloakService


letters = string.ascii_lowercase
name = str(''.join(random.choice(letters) for _ in range(10))).lower()
description = str(''.join(random.choice(letters) for _ in range(40))).lower()
attributes = {'alias': [description]}


def test_get_funcionario_username(get_edat_keycloak_service: EdatKeycloakService, get_usernames: List[str]):

    for username in get_usernames:
        user = get_edat_keycloak_service.get_user_username(username)

        assert user
        assert isinstance(user, DataKeycloakUser)
        assert user.attributes
        assert user.attributes.employeeNumber


def test_get_funcionario_employeed(get_edat_keycloak_service: EdatKeycloakService, get_matriculas: List[int]):

    for matricula in get_matriculas:
        user = get_edat_keycloak_service.get_user_employeeNumber(matricula)

        assert user
        assert isinstance(user, DataKeycloakUser)
        assert user.attributes
        assert user.attributes.employeeNumber


def test_get_roles(get_edat_keycloak_service: EdatKeycloakService):
    roles = get_edat_keycloak_service.get_roles()

    assert len(roles) > 0


def test_get_groups(get_edat_keycloak_service: EdatKeycloakService):
    groups = get_edat_keycloak_service.get_groups()

    assert len(groups) > 0

    for group in groups:
        assert isinstance(group, DataKeycloakGroup)


def test_crud_group(get_edat_keycloak_service: EdatKeycloakService):
    letters = string.ascii_lowercase
    name = str(''.join(random.choice(letters) for _ in range(10))).upper()

    get_edat_keycloak_service.create_group(name=name)

    group = get_edat_keycloak_service.get_group_by_path(path=name)

    assert group
    assert isinstance(group, DataKeycloakGroup)

    deleted= get_edat_keycloak_service.delete_group(group.id)
    group = get_edat_keycloak_service.get_group_by_path(path=name)

    assert deleted
    assert not group


def test_create_role(get_edat_keycloak_service: EdatKeycloakService):
    role = CreateRealmRole(name=name, description=description, attributes=attributes)
    role_created = get_edat_keycloak_service.create_role(role=role)
    assert role_created


def test_get_role(get_edat_keycloak_service: EdatKeycloakService):
    role = get_edat_keycloak_service.get_role_name(name=name)
    assert role


def test_delete_role(get_edat_keycloak_service: EdatKeycloakService):
    deleted = get_edat_keycloak_service.delete_role_id(id=name)
    assert deleted
