from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.type_adapter import TypeAdapter


class TipoUsuario(str, Enum):
    """Classe enum de tipo de usuário"""

    DOCENTE = "faculty"
    FUNCIONARIO = "staff"
    ALUNO = "student"
    ALUNO_COTIL = "ALUNO COTIL"
    ALUNO_COTUCA = "ALUNO COTUCA"
    FUNCAMP = "funcamp"

    def __str__(self) -> str:
        return str(self.value)


def obter_tipo_usuario_aluno(usuario):
    if usuario.nome_curso:
        if str(usuario.nome_curso).lower().startswith("técnico") or str(
            usuario.nome_curso.lower().startswith("tecnico")
        ):
            match usuario.unidade.lower():
                case "cotil":
                    return TipoUsuario.ALUNO_COTIL
                case "cotuca":
                    return TipoUsuario.ALUNO_COTUCA
        else:
            return TipoUsuario.ALUNO

    return TipoUsuario.ALUNO


def camel_to_snake(name: str) -> str:
    """Converte camelCase para snake_case."""
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Usuario(BaseModel):
    model_config = ConfigDict(
        alias_generator=camel_to_snake,  # converte automaticamente camelCase → snake_case
        populate_by_name=True,  # permite acessar tanto por camelCase quanto por snake_case
        extra="ignore",  # ignora campos inesperados
    )

    nome: str = Field(..., description="Nome do usuário")
    identificador: int = Field(
        ..., description="Identificador do usuário, matricula ou ra"
    )
    email: Optional[str] = Field(None, description="Nome do usuário")
    unidade: Optional[str] = Field(
        None, description="Unidade, Centro, Instituto ou Faculdade do usuário"
    )
    local: Optional[str] = Field(None, description="Local dentro da Unidade")
    nome_local: Optional[str] = Field(None, description="Nome da local")
    nome_unidade: Optional[str] = Field(None, description="Nome da unidade")
    cargo: str = Field(..., description="cargo ou curso do usuário")
    nome_sindicato: Union[str, None] = Field(
        default=None,
        exclude=True,
        alias="nomeSindicato",
        description="Tipo de sindicato do usuário [Apenas disponivel na instanciação da classe]",
    )
    nome_curso: Union[str, None] = Field(
        default=None,
        exclude=True,
        alias="nomeCurso",
        description="Nome do curso do usuário [Apenas disponivel na instanciação da classe]",
    )
    telefone: Optional[Union[str, int]] = Field(
        default=None, description="telefone/ ramal do usuário"
    )
    username: Optional[str] = Field(default=None, description="username do usuário")
    designacao: Union[Optional[str], None] = Field(
        default=None, description="designacao do usuario. Ex.: Gratificação"
    )
    tipo_usuario: Union[TipoUsuario, None] = Field(
        default=None, alias="tipo_usuario", description="Tipo de Membro do usuário"
    )

    @model_validator(mode="before")
    def antes(cls, values):
        if "email" not in values:
            values["email"] = "não informado"

        if values["email"] in ["", " ", "  ", None]:
            values["email"] = "não informado"

        if isinstance(values["email"], int):
            values["email"] = "não informado"

        if "telefone" not in values:
            values["telefone"] = "não informado"

        if values["telefone"] in ["", " ", "  ", None]:
            values["telefone"] = "não informado"

        if values["identificador"] == values["telefone"]:
            values["telefone"] = "não informado"

        return values

    @model_validator(mode="after")
    def ajustar_campos(self):
        # Ajustar nome
        self.nome = str(self.nome).title()
        self.cargo = str(self.cargo).title()
        self.nome_unidade = str(self.nome_unidade).title()
        self.nome_local = str(self.nome_local).title()

        # ajustar o tipo de usuário
        match str(self.nome_sindicato).strip().lower():
            case "funcamp":
                self.tipo_usuario = TipoUsuario.FUNCAMP
            case "esu, docente":
                self.tipo_usuario = TipoUsuario.DOCENTE
            case "clt, docente":
                self.tipo_usuario = TipoUsuario.DOCENTE
            case "esu, não docente":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "esu aposentado":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "clt aposentado":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "clt, não docente":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "trabalhador s/ vínculo empregatício / estatutário - não docente":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "trabalhador s/ vínculo empregatício / estatutário - docente":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "trabalhador sem vínculo empregatício":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "bolsista - extra quadro":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case "tercerizado":
                self.tipo_usuario = TipoUsuario.FUNCIONARIO
            case _:
                self.tipo_usuario = obter_tipo_usuario_aluno(self)

        # ajustar o username
        if str(self.email).lower() not in ["email nao ativo", "não informado"]:
            self.username = str(self.email).split("@")[0]
        else:
            self.username = None

        # remover o campo desnecessário
        delattr(self, "nome_sindicato")
        delattr(self, "nome_curso")

        return self


class UnidadeSchema(BaseModel):
    numeroLotacao: int = Field(..., description="Número da lotação da unidade")
    unidade: str = Field(..., description="Sigla da unidade")
    nomeUnidade: str = Field(
        ..., description="Nome da unidade em caixa alta sem acentuação"
    )
    lotacao: str = Field(..., description="Código da lotação da unidade")
    nomeUnidadeAcentuada: Optional[str] = Field(
        None, description="Nome da unidade formatado e acentuado"
    )
    tipoUnidade: Optional[str] = Field(..., description="Tipo da unidade")
    categoriaUnidade: Optional[str] = Field(..., description="Categoria da Unidade")
    siglaArea: Optional[str] = Field(..., description="Sigla da área da unidade")
    descricaoArea: Optional[str] = Field(..., description="Descrição da unidade")

    @model_validator(mode="before")
    def antes(cls, values):
        if "siglaArea" in values and values["siglaArea"] in ["", " ", "  ", "null"]:
            values["siglaArea"] = None

        if "lotacao" not in values:
            values["lotacao"] = values.get("codigoLocal", "não informado")

        if "descricaoArea" not in values:
            values["descricaoArea"] = None

        if "numeroLotacao" not in values:
            values["numeroLotacao"] = values.get("numeroUnidade", 0)

        return values


class CursoSchema(BaseModel):
    dataGeracao: datetime = Field(
        ...,
        description="Data de quanto o registro foi processado pelo sistema de importação de tabelas",
    )
    ultimoCatalogoVigente: int = Field(
        ..., description="Último ano do catálogo vigente"
    )
    siglaOrgao: str = Field(..., description="Sigla do orgão ao qual o curso pertence")
    codigoCurso: int = Field(..., description="Código do curso")
    nomeCurso: str = Field(..., description="Nome do curso")
    nomeUnidade: str = Field(
        ..., description="Nome da unidade ao qual o curso pertence"
    )


class CursoDacSchema(CursoSchema):
    siglaOrgaoCatalogo: str = Field(str, description="Sigla do órgão do catálogo")
    nivelCurso: str = Field(..., description="Nível do curso")
    descAreaCurso: str = Field(..., description="Descrição da área do curso")
    tipoTurnoCurso: str = Field(..., description="Tipo de turno do curso")
    nomeUnidadeAcentuada: str = Field(
        ..., description="Nome da unidade com acentuação ao qual o curso pertence"
    )
    coordenadoria: str = Field(
        ..., description="Nome da coordenadoria ao qual o curso pertence"
    )
    classificacaoCurso: Optional[str] = Field(..., description="Classificação do curso")
    nomeCursoAnuario: Optional[str] = Field(
        default=None, description="Nome do curso do anuário"
    )
    especialidadeAnuario: Optional[str] = Field(
        default=None, description="Especialidade do anuário"
    )
    siglaOrgaoAnuario: Optional[str] = Field(
        ..., description="Sigla do orgão do anuário"
    )


class CursoTecnicoSchema(BaseModel):
    totalDeMatriculadosCurso: Optional[int] = Field(
        default=None, description="Quantidade de alunos matriculados"
    )


# Tipo de lista de usuário para facilitar o parse do pydantic
UsuarioList = TypeAdapter(List[Usuario])

# Tipo de lista de unidade para facilitar o parse do pydantic
UnidadeSchemaList = TypeAdapter(List[UnidadeSchema])

# Tipo de lista de cursos academicos para facilitar o parse do pydantic
CursoList = TypeAdapter(List[CursoDacSchema])

# Tipo de lista de cursos técnicos para facilitar o parse do pydantic
CursoTecnicoList = TypeAdapter(List[CursoTecnicoSchema])
