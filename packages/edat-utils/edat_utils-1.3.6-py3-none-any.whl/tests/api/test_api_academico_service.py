from typing import List, Union
from edat_utils.api import ApiAcademicoService
from edat_utils.api.models import TipoUsuario, Usuario


def test_get_alunos(get_api_academico_service: ApiAcademicoService):
    query = f'startWith: {{nome_civil_aluno: "João"}}'  # noqa
    alunos: Union[List[Usuario], None] = get_api_academico_service.get(query=query)

    if not alunos:
        assert False

    assert len(alunos) > 0

    for aluno in alunos:
        assert aluno.tipo_usuario == TipoUsuario.ALUNO
        assert aluno.nome
        assert aluno.identificador
        assert aluno.email


def test_get_aluno_sem_duplicacao(get_api_academico_service: ApiAcademicoService):
    query = f"eq: {{ra: 103752}}"  # noqa
    alunos: Union[List[Usuario], None] = get_api_academico_service.get(query=query)

    if not alunos:
        assert False

    assert len(alunos) == 1

    for aluno in alunos:
        assert aluno.tipo_usuario == TipoUsuario.ALUNO
        assert aluno.nome
        assert aluno.identificador
        assert aluno.email
        assert not aluno.designacao
        assert not getattr(aluno, "nome_sindicato", None)
        assert not getattr(aluno, "nomeSindicato", None)
        assert not getattr(aluno, "nome_curso", None)
        assert not getattr(aluno, "nomeCurso", None)
