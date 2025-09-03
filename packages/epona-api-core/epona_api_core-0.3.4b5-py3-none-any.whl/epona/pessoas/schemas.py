from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic.creator import pydantic_model_creator

from .models import Pessoa

PessoaSchema = pydantic_model_creator(Pessoa, module="Pessoa")


class TipoEnum(str, Enum):
    FISICA = "FISICA"
    JURIDICA = "JURIDICA"


class TipoDocumentoEnum(str, Enum):
    REGISTRO_GERAL = "REGISTRO_GERAL"
    INSCRICAO_ESTADUAL = "INSCRICAO_ESTADUAL"


class PessoaPayloadSchema(BaseModel):
    pai: Optional[str] = ""  # TODO: verificar uso
    cadastro: Optional[str] = ""
    cpf_cnpj: str
    documento: Optional[str] = ""
    email: Optional[str] = ""
    nome: str
    nome_fantasia: Optional[str] = ""
    licenciavel: Optional[bool] = False
    matriz: Optional[bool] = False
    tipo: TipoEnum
    tipo_cadastro: Optional[str] = ""
    tipo_documento: Optional[TipoDocumentoEnum] = None


class PessoaResponseSchema(PessoaPayloadSchema):
    id: str
    suuid: str


class TipoTelefoneEnum(str, Enum):
    RESIDENCIAL = "RESIDENCIAL"
    COMERCIAL = "COMERCIAL"
    CELULAR_PESSOAL = "CELULAR_PESSOAL"
    CELULAR_TRABALHO = "CELULAR_TRABALHO"


class InfoContatoPayloadSchema(BaseModel):
    email: Optional[str] = None
    pessoa_id: str
    telefone: Optional[str] = None
    tipo: Optional[TipoTelefoneEnum] = None


class InfoContatoResponseSchema(InfoContatoPayloadSchema):
    id: str
    suuid: str
    pessoa_suuid: Optional[str]


class PessoaMatrizSchema(PessoaResponseSchema):
    responsavel: str
    contatos: Optional[List[InfoContatoResponseSchema]]
