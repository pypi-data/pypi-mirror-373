import logging
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field
from pydantic.type_adapter import TypeAdapter
import requests


logger = logging.getLogger(__name__)


class PermissaoException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return self.__str__()


class DataCreateRole(BaseModel):
    username: str
    permissao: str
    id_avaliacao: str


class DataRealmMappings(BaseModel):
    id: str
    name: str
    description: str
    composite: bool
    clientRole: bool
    containerId: str
    attributes: Optional[dict] = Field(None)


class DataKeycloakAccess(BaseModel):
    view: Optional[bool] = Field(None)
    manage: Optional[bool] = Field(None)
    mapRoles: Optional[bool] = Field(None)
    impersonate: Optional[bool] = Field(None)
    manageGroupMembership: Optional[bool] = Field(None)


class DataKeycloakAttributes(BaseModel):
    ou: List[str] = Field(...)
    LDAP_ID: List[str] = Field(...)
    employeeType: List[str] = Field(...)
    LDAP_ENTRY_DN: List[str] = Field(...)
    employeeNumber: List[str] = Field(...)
    departmentNumber: List[str] = Field(...)
    eduPersonAffiliation: List[str] = Field(...)


class DataKeycloakUser(BaseModel):
    id: Optional[str]
    totp: Optional[bool]
    enabled: Optional[bool]
    username: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    emailVerified: Optional[bool]
    createdTimestamp: Optional[int]
    notBefore: Optional[int] = Field(None)
    federationLink: Optional[str] = Field(None)
    access: Optional[DataKeycloakAccess] = Field(None)
    requiredActions: Optional[List[str]] = Field(None)
    attributes: Optional[DataKeycloakAttributes] = Field(None)
    disableableCredentialTypes: Optional[List[str]] = Field(None)


class DataKeycloakGroup(BaseModel):
    id: str
    name: str
    path: str
    subGroups: Optional[List] = Field(None)
    clientRoles: Optional[dict] = Field(None)
    realmRoles: Optional[List[DataRealmMappings]] = Field(None)
    attributes: Optional[dict] = Field(None)


class CreateRealmRole(BaseModel):
    name: str
    description: str
    attributes: Any


# Tipo lista grupo
GroupList = TypeAdapter(List[DataKeycloakGroup])

# Tipo lista de usuarios
UserList = TypeAdapter(List[DataKeycloakUser])


class EdatKeycloakService():

    def __init__(self, base_url: str, client_id: str, client_secret: str, realm: str = 'dev'):
        self.KEYCLOAK_REALM = realm
        self.ADMIN_LOGIN_URL = f'{base_url}/realms/{realm}/protocol/openid-connect/token'
        self.BASE_KEYCLOAK_URL = f'{base_url}/admin/realms'
        self.USER_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/users'
        self.GROUP_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/groups'
        self.GROUP_BY_PATH_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/group-by-path'
        self.REALM_ROLES_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/roles'
        self.REALM_ROLE_ID_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/roles-by-id'
        self.ROLE_USER_URL = f'{self.BASE_KEYCLOAK_URL}/{realm}/users/<id>/role-mappings'

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "openid"
        }

        response = requests.post(url=self.ADMIN_LOGIN_URL, data=data)

        if 'access_token' in response.json():
            token = response.json()['access_token']
            self.__headers = {'Authorization': f'Bearer {token}',
                              'content-type': 'application/json'}
        else:
            message = f'Erro ao autenticar com o keycloak'
            logger.error(msg=f'Erro ao autenticar com o keycloak\t{response.json()}')
            raise Exception(message)

    def get_users(self) -> List[DataKeycloakUser]:
        response = requests.get(url=self.USER_URL, headers=self.__headers)
        return [DataKeycloakUser(**user) for user in response.json()]

    def get_user_id(self, id: str):
        url = f'{self.USER_URL}/{id}'
        response = requests.get(url=url, headers=self.__headers)
        try:
            return DataKeycloakUser(**response.json())
        except Exception as e:
            message = f'Erro ao buscar usuário com id {id}'
            logger.error(msg=f'{message}\tresponse={response.json()}\terror={e}')
            raise PermissaoException(message)

    def get_user_username(self, username: str) -> DataKeycloakUser:
        try:
            int(username)
            _username = username if len(username) > 5 else f'0{username}'
        except Exception:
            _username = username

        response = requests.get(url=self.USER_URL, headers=self.__headers, params={'q': f'username:{_username}', 'exact': True})

        if len(response.json()) == 0:
            message = f'Usuário com username {username} não encontrado no sistema'
            logger.error(msg=f'{message}')
            raise PermissaoException(message)
        try:
            if len(response.json()) == 0:
                message = f'Usuário com username {username} não encontrado no sistema na lista de usuários'
                logger.error(msg=f'{message}')
                raise PermissaoException(message)

            return DataKeycloakUser(**response.json()[0])

        except Exception as e:
            message = f'Erro ao buscar usuário com username {username}'
            logger.error(msg=f'{message}\tresponse={response.json()}\terro={e}')
            raise PermissaoException(message)

    def get_user_employeeNumber(self, employee_number: int) -> Union[DataKeycloakUser, None]:
        response = requests.get(url=self.USER_URL, headers=self.__headers, params={
                                'q': f'employeeNumber:{employee_number}', 'exact': True})
        try:
            if len(response.json()) == 0:
                return None
            user = response.json()[0]
            return DataKeycloakUser(**user)
        except Exception as e:
            logger.error(msg=f'Erro ao buscar usuário com número {employee_number}\tresponse={response.json()}\terro={e}')
            return None

    def create_role(self, role: CreateRealmRole) -> bool:
        """ Método para criar uma nova role
            :param role: Objeto do tipo CreateRealmRole
            :return: True or False
        """
        response = requests.post(url=self.REALM_ROLES_URL, headers=self.__headers, json=role.model_dump())
        try:
            return response.status_code in {201, 409}
        except Exception as e:
            logger.error(msg=f'Erro ao criar role no realm {self.KEYCLOAK_REALM}\tresponse={response.json()}\terro={e}')
            return False

    def get_roles(self):
        params = {'briefRepresentation': False}
        response = requests.get(url=self.REALM_ROLES_URL, headers=self.__headers, params=params)
        try:
            return [DataRealmMappings(**role) for role in response.json()]
        except Exception as e:
            logger.warning(msg=f'Erro ao buscar roles do realm {self.KEYCLOAK_REALM}\tresponse={response.json()}\terro={e}')
            return []

    def get_role_id(self, id: str) -> Optional[DataRealmMappings]:
        url = f'{self.REALM_ROLE_ID_URL}/{id}'
        params = {'briefRepresentation': False}

        response = requests.get(url=url, headers=self.__headers, params=params)
        if response.status_code == 200:
            role = DataRealmMappings(**response.json())
            return role
        else:
            logger.error(msg=f'Erro ao buscar a role {id} no keycloak\tresponse={response.json()}')
            return None

    def delete_role_id(self, id: str) -> bool:
        """ Método para remover uma role
            :param id: id / name da role
            :return: True or False
        """
        url = f'{self.REALM_ROLES_URL}/{id}'
        response = requests.delete(url=url, headers=self.__headers)
        return response.status_code in {204}

    def get_role_name(self, name: str):
        url = f'{self.REALM_ROLES_URL}/{name}'
        params = {'briefRepresentation': False}

        response = requests.get(url=url, headers=self.__headers, params=params)
        if response.status_code == 200:
            return DataRealmMappings(**response.json())
        else:
            logger.error(msg=f'Erro ao buscar a role {name} no keycloak\tresponse={response.json()}')
            return None

    def get_roles_by_user(self, id: str):
        url = f'{self.ROLE_USER_URL}'.replace('<id>', id)
        params = {'briefRepresentation': False}

        response = requests.get(url=url, headers=self.__headers, params=params)
        try:
            return [DataRealmMappings(**role) for role in response.json()['realmMappings']]
        except Exception as e:
            logger.warning(msg=f'Erro ao buscar roles do usuário {id}\tresponse={response.json()}\terro={e}')
            return []

    def assign_user_role(self, user_id: str, role: DataRealmMappings) -> bool:
        url = f'{self.ROLE_USER_URL}/realm'.replace('<id>', user_id)
        response = requests.post(url=url, headers=self.__headers, json=[role.__dict__])

        if response.status_code == 204:
            logger.info(msg=f'Perfil {role.name} assinado para o usuário {user_id} com sucesso.')
            return True

        else:
            logger.error(msg=f'Erro ao tentar assinar o perfil {role.name} ao usuário com id {user_id}.\tresponse={response.json()}')
            return False

    def delete_user_role(self, user_id: str, role: DataRealmMappings) -> bool:
        url = f'{self.ROLE_USER_URL}/realm'.replace('<id>', user_id)
        response = requests.delete(url=url, headers=self.__headers, json=[role.__dict__])
        if response.status_code == 204:
            logger.info(msg=f'Perfil {role.name} REMOVIDO para o usuário {user_id} com sucesso.')
            return True
        else:
            logger.error(msg=f'Erro ao tentar REMOVER o perfil {role.name} do usuário com id {user_id}. body={response.json()}')
            return False

    def get_groups(self) -> List[DataKeycloakGroup]:
        response = requests.get(url=self.GROUP_URL, headers=self.__headers)
        if response.status_code == 200:
            return GroupList.validate_python(response.json())
        return []

    def get_groups_by_path(self, path: str) -> DataKeycloakGroup | List:
        response = requests.get(url=self.GROUP_BY_PATH_URL+path, headers=self.__headers)
        if response.status_code == 200:
            return DataKeycloakGroup(**response.json())
        return []

    def get_group(self, id: str) -> Optional[DataKeycloakGroup]:
        url = f'{self.GROUP_URL}/{id}'
        response = requests.get(url=url, headers=self.__headers)
        if response.status_code == 200:
            return DataKeycloakGroup(**response.json())
        return None

    def get_group_by_path(self, path: str) -> Optional[DataKeycloakGroup]:
        _path = path if str(path).startswith('/') else f'/{path}'
        url = f'{self.GROUP_URL}{_path}'.replace('groups', 'group-by-path')
        response = requests.get(url=url, headers=self.__headers)
        if response.status_code == 200:
            return DataKeycloakGroup(**response.json())
        return None

    def get_members_by_group(self, id: str) -> List[DataKeycloakUser]:
        url = f'{self.GROUP_URL}/{id}/members'
        response = requests.get(url=url, headers=self.__headers)
        if response.status_code == 200:
            return UserList.validate_python(response.json())
        return []

    def insert_member_group(self, id_group: str, id_user: str) -> bool:
        url = f'{self.USER_URL}/{id_user}/groups/{id_group}'
        response = requests.put(url=url, headers=self.__headers)
        if response.status_code == 204:
            logger.info(msg=f'usuário {id_user} inserido no grupo {id_group}')
            return True

        message = f'Erro ao inserir o usuário {id_user} no grupo {id_group}'
        logger.error(msg=f'{message}\terro={response.json()}')
        raise Exception(message)

    def get_roles_by_group(self, id: str) -> List[DataRealmMappings]:
        url = f'{self.GROUP_URL}/{id}/role-mappings'
        response = requests.get(url=url, headers=self.__headers)
        if response.status_code == 200:
            content = response.json()['realmMappings']
            return [DataRealmMappings(**role) for role in content]
        raise Exception(f'Erro ao buscar roles do grupo {id}')

    def delete_member_group(self, id_group: str, id_user: str) -> bool:
        url = f'{self.USER_URL}/{id_user}/groups/{id_group}'
        response = requests.delete(url=url, headers=self.__headers)
        if response.status_code == 204:
            logger.info(
                msg=f'usuário {id_user} REMOVIDO do grupo {id_group}')
            return True
        raise Exception(
            f'Erro ao remover o usuário {id_user} no grupo {id_group}')

    def assign_role_group(self, id_group: str, role: DataRealmMappings) -> bool:
        url = f'{self.GROUP_URL}/{id_group}/role-mappings/realm'
        logger.info(msg=f'assinando a role {role.name} no grupo {id_group}')
        response = requests.post(
            url=url, headers=self.__headers, json=[role.__dict__])
        if response.status_code == 204:
            logger.info(
                msg=f'Permissão {role.name} inserida no grupo {id_group}.')
            return True
        else:
            message = f'Erro ao tentar inserir a permissão {role.name} ao grupo {id_group}'
            logger.error(
                msg=f'{message}\tresponse={response.json()}')
            return False

    def create_group(self, name: str) -> bool:
        response = requests.post(
            url=self.GROUP_URL, headers=self.__headers, json={'name': name})

        return response.status_code == 201

    def delete_group(self, id: str) -> bool:
        url = f'{self.GROUP_URL}/{id}'
        response = requests.delete(url=url, headers=self.__headers)

        return response.status_code == 204

    def create_children_group(self, id_parent: str, name: str) -> bool:
        url = f'{self.GROUP_URL}/{id_parent}/children'
        response = requests.post(
            url=url, headers=self.__headers, json={'name': name})

        return response.status_code == 201
