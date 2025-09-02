from abc import ABC, abstractmethod


class BaseApiGraphiQL(ABC):

    def __init__(self, url: str, token: str | None):
        self._base_url = url
        self._head_query = None
        self._tail_query = None
        self._headers = None

        if not str(token).startswith('Bearer '):
            self._headers = {'Authorization': f'Bearer {token}'}
        else:
            self._headers = {'Authorization': token}

    @abstractmethod
    def get(self, query: str):
        """ Método para obter usuários

            param query: string contento a query graphiql de pesquisa
            return: Lista de usuários

            Exemplo:
                query = f'in: {{ra: {[103752, 103750, 104589, 105891, 107921]}}}'
        """
        pass
        
