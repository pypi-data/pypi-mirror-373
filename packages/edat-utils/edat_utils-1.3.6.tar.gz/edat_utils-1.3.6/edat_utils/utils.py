import base64
import json

from strawberry.types import Info
import re
from sqlalchemy.engine.row import Row
from typing import List, Optional, Union
from edat_utils.schema import EdatGrouped

EDAT_USER = 'X-EDAT-USER'


class EdatUtils:
    @staticmethod
    def get_fields(info: Info):
        selected_fields = {item.name for field in info.selected_fields
                           for selection in field.selections for item in selection.selections}
        return selected_fields
    
    @staticmethod
    def get_user(info: Info):
        request = info.context['request']
        user =  None
        if EDAT_USER in request.headers:
            user = request.headers[EDAT_USER]
        return user

    @staticmethod
    def get_real_ip(x_forwarded_for: Optional[str]) -> str | None:
        """ Método para obter o ip do cliente

            :param x_forwarded_for: header informado na requisição nos ambientes de prod e homolog
            :return: ip em formato de string ou nulo
        """
        if not x_forwarded_for:
            return None

        ip_list = list(str(x_forwarded_for).split(','))

        if len(ip_list) == 0:
            return None

        return ip_list[0]

    @staticmethod
    def get_username(token: str = '') -> Union[str, None]:
        """ Método para obter o usuário presente no token

            :param token: str/token
            :return: username do usuário presente no token
        """
        if not token:
            return None

        if 'Bearer' in token or 'bearer' in token:
            token = token.replace('Bearer', '').strip()

        _, payload, _ = token.split('.')
        payload_bytes = base64.urlsafe_b64decode(payload + '===')
        payload_data = json.loads(payload_bytes)
        return payload_data['preferred_username']

    def get_table_name(info: Info):
        name = list(info.return_type.__dict__['_type_definition'].type_var_map.values())[0].__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def get_list(info: Info, rows: List[Row]):
        obj_list = []

        class_ = list(info.return_type.__dict__['_type_definition'].type_var_map.values())[0]
        args = class_.__init__.__code__.co_varnames[1:]

        for row in rows:
            params = row._asdict()
            params_to_pass = {argname: params[argname] if argname in params else None  for argname in args}    
            instance = class_(**params_to_pass)
            obj_list.append(instance)
        return obj_list
    
    def is_grouped(info: Info):
        class_ = list(info.return_type.__dict__['_type_definition'].type_var_map.values())[0]
        return issubclass(class_, EdatGrouped)
