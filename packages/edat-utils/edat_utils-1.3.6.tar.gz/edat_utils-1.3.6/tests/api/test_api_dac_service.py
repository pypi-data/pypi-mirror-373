from typing import List, Union

from edat_utils.api.api_dac_service.service import ApiDacService
from edat_utils.api.models import CursoDacSchema


def test_get_cursos_academicos(get_api_dac_service: ApiDacService):
    cursos: Union[List[CursoDacSchema], None] = get_api_dac_service.get(query='')

    if not cursos:
        assert False

    assert len(cursos) > 0
    for curso in cursos:
        assert curso.nomeCurso
        assert curso.nomeUnidade
        assert curso.nomeUnidadeAcentuada
