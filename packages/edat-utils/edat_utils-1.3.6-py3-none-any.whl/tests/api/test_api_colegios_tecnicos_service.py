from typing import List, Union
from edat_utils.api.api_colegios_service.service import ApiColegiosTecnicosService
from edat_utils.api.models import TipoUsuario, Usuario


def test_get_alunos_colegios(get_api_colegios_tecnicos_service: ApiColegiosTecnicosService):
    query = f'notNull: {{nome_aluno: ""}}'
    alunos: Union[List[Usuario], None] = get_api_colegios_tecnicos_service.get(query=query)

    if not alunos:
        assert False

    assert len(alunos) > 0

    for aluno in alunos:
        assert aluno.tipo_usuario in [TipoUsuario.ALUNO_COTIL, TipoUsuario.ALUNO_COTUCA]
        assert aluno.nome
        assert aluno.email
        assert aluno.designacao == None
