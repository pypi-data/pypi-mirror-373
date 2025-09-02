from typing import List, Union
from edat_utils.api import ApiFuncionarioService
from edat_utils.api.models import TipoUsuario, Usuario


def test_get_funcionarios(get_api_funcionario_service: ApiFuncionarioService):
    query = f'startWith: {{nome: "MaR"}}'  # noqa
    funcionarios: Union[List[Usuario], None] = get_api_funcionario_service.get(
        query=query
    )

    if not funcionarios:
        assert False

    # --- Validar se houve resposta
    assert len(funcionarios) > 0

    # --- Validar todos os registros
    for funcionario in funcionarios:
        print(funcionario)
        assert funcionario.tipo_usuario in [
            TipoUsuario.FUNCIONARIO,
            TipoUsuario.FUNCAMP,
            TipoUsuario.DOCENTE,
        ]

        assert funcionario.email
        assert funcionario.telefone
        assert funcionario.unidade
        assert funcionario.nome_unidade
        assert funcionario.local
        assert funcionario.nome_local

        assert not getattr(funcionario, "nome_sindicato", None)
        assert not getattr(funcionario, "nomeSindicato", None)
        assert not getattr(funcionario, "nome_curso", None)
        assert not getattr(funcionario, "nomeCurso", None)
