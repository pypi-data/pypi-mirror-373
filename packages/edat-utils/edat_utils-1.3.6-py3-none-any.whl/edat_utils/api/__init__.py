"""
Api
==============

Descrição:
-----------
Este pacote fornece funcionalidades para conectar com os serviços graphiql auxiliares. Ele inclui módulos para obter dados de funcionários, docentes, dicentes, unidades e vida acadêmica.

Módulos:
--------
- api_funcionario_service: Obtem dados de funcionários

Exemplo de Uso:
---------------
```python
from edat_utils.api import ApiFuncionarioService

# Exemplo de como usar ApiFuncionarioService
service = ApiFuncionarioService(token='<token>', url='<url-da-api>')

query = f'in: {{matricula: {matriculas}}}, eq: {{ situacao: "Ativo"}}'
funcionarios = service.get(query=query)

for f in funcionarios:
    print(f)
```
"""

from edat_utils.api.api_academico_service import ApiAcademicoService
from edat_utils.api.api_colegios_service import ApiColegiosTecnicosService
from edat_utils.api.api_funcionario_service import ApiFuncionarioService
from edat_utils.api.api_unidade_service import ApiUnidadeService
from edat_utils.api.api_lotacao_service import ApiLotacaoService
from edat_utils.api.api_dac_service import ApiDacService
from edat_utils.api.base import BaseApiGraphiQL
from edat_utils.api.custom_exceptions import *
from edat_utils.api.models import *
