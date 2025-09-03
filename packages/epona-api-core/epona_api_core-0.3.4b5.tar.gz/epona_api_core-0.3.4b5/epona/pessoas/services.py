import asyncio
import logging
import os
from datetime import datetime
from typing import List, Union

from fastapi import HTTPException
from openpyxl import Workbook
from pydantic import ValidationError

from epona.auth.schemas import UserSchema
from epona.common import create_suuid
from epona.pessoas import models, schemas

env = os.getenv("ENVIRONMENT", "dev")


async def save(payload: schemas.PessoaPayloadSchema, user: UserSchema) -> str:
    """Cria e salva uma pessoa ou empresa no banco de dados e retorna seu id"""
    attempt = 0
    while attempt < 3:
        attempt += 1
        try:
            pessoa = models.Pessoa(
                client_id=user.client_id,
                cadastro=payload.cadastro,
                cpf_cnpj=payload.cpf_cnpj,
                documento=payload.documento,
                email=payload.email,
                nome=payload.nome,
                nome_fantasia=payload.nome_fantasia,
                pessoa_suuid=payload.pai,
                tipo=payload.tipo,
                tipo_cadastro=payload.tipo_cadastro,
                tipo_documento=payload.tipo_documento,
                suuid=create_suuid(),
            )
            if env == "prod" and not validate_cpf_cnpj(pessoa):
                cpf_cnpj = "CPF" if pessoa.tipo == "FISICA" else "CNPJ"
                raise HTTPException(422, f"{cpf_cnpj} inválido")
            if payload.licenciavel and payload.tipo == "JURIDICA":
                pessoa.licenciavel = payload.licenciavel
            if payload.matriz and payload.tipo == "JURIDICA":
                pessoa.matriz = payload.matriz
            await pessoa.save()
            return pessoa.suuid
        except Exception as err:
            logging.error(f"Falha ao tentar salvar pessoa: {attempt}/3\n{str(err)}")
            await asyncio.sleep(attempt * 5)


async def update(
    payload: schemas.PessoaPayloadSchema, user: UserSchema
) -> Union[int, None]:
    """Altera as informações de uma pessoa ou empresa e retorna seu id"""
    pessoa = await models.Pessoa.filter(
        cpf_cnpj=payload.cpf_cnpj, client_id=user.client_id
    ).first()
    if not pessoa:
        pessoa = await models.Pessoa.filter(
            cadastro=payload.cadastro,
            tipo_cadastro=payload.tipo_cadastro,
            client_id=user.client_id,
        ).first()
        if not pessoa:
            return None
    pessoa.nome = payload.nome if payload.nome else pessoa.nome
    pessoa.cpf_cnpj = payload.cpf_cnpj if payload.cpf_cnpj else pessoa.cpf_cnpj
    pessoa.email = payload.email if payload.email else pessoa.email
    pessoa.documento = payload.documento if payload.documento else pessoa.documento
    pessoa.tipo_documento = (
        payload.tipo_documento if payload.tipo_documento else pessoa.tipo_documento
    )
    pessoa.nome_fantasia = (
        payload.nome_fantasia if payload.nome_fantasia else pessoa.nome_fantasia
    )
    pessoa.created_at = datetime.fromisoformat(str(pessoa.created_at)[:26])
    pessoa.updated_at = datetime.utcnow()
    if payload.tipo == "JURIDICA":
        if payload.licenciavel is True:
            pessoa.licenciavel = True
        if payload.matriz is True:
            pessoa.matriz = True
    attempt = 0
    while attempt < 3:
        attempt += 1
        try:
            await pessoa.save()
            return pessoa.suuid
        except Exception as err:
            logging.error(
                f"Falha ao atualizar pessoa. Tentativa: {attempt}/3.\n{str(err)}"
            )
            await asyncio.sleep(5 * attempt)


async def save_xlsx(
    wb: Workbook, user: UserSchema
) -> List[schemas.PessoaResponseSchema]:
    """Salva pessoas a partir de uma planilha xlsx"""
    await asyncio.sleep(0)
    pessoas = []
    try:
        for i, line in enumerate(wb["Pessoas"].iter_rows()):
            if i == 0 or not line[0].value:
                continue
            payload = schemas.PessoaPayloadSchema(
                **{
                    "cpf_cnpj": str(line[0].value).strip(),
                    "nome": line[1].value.strip(),
                    "tipo_documento": line[2].value,
                    "documento": str(line[3].value),
                    "tipo": line[4].value,
                    "email": line[5].value,
                    "nome_fantasia": line[6].value,
                    "licenciavel": line[7].value,
                    "matriz": line[8].value,
                }
            )
            if env == "prod" and not validate_cpf_cnpj(payload):
                raise ValueError
            pessoas.append(payload)
    except (ValueError, KeyError, ValidationError):
        raise ValueError(
            f"Erro na linha {i+1}. Verifique se todas a colunas estão "
            f"preenchidas e com valores válidos, inclusive CPF/CNPJ"
        )
    except IndexError:
        raise ValueError(
            "Número de colunas na planilha é menor que o esperado. "
            "Utilize o arquivo modelo."
        )
    armazenadas = []
    for pessoa in pessoas:
        result = await save(pessoa, user)
        if result:
            armazenadas.append(
                schemas.PessoaResponseSchema(
                    **{"id": result, "suuid": result, **pessoa.model_dump()}
                )
            )
    return armazenadas


async def get(pk: str, user: UserSchema) -> Union[schemas.PessoaSchema, None]:
    """retorna informações de uma pessoa ou empresa filtrada por id"""
    pessoa = await models.Pessoa.filter(suuid=pk, client_id=user.client_id).first()
    if not pessoa:
        return None
    return schemas.PessoaSchema(**dict(pessoa))


async def get_all(user: UserSchema, limit=100) -> List:
    """Retorna todas as pessoas e empresas vinculádas a um client_id"""
    pessoas = (
        await models.Pessoa.filter(client_id=user.client_id)
        .all()
        .order_by("-created_at")
        .limit(limit)
        .values()
    )
    pessoas_list = [pessoa for pessoa in pessoas]
    return pessoas_list


async def delete(pk: str, user: UserSchema) -> bool:
    """apaga uma pessoa ou empresa do banco por id"""
    pessoa = await models.Pessoa.filter(suuid=pk, client_id=user.client_id).first()
    if pessoa:
        await pessoa.delete()
        return True
    return False


async def by_name(nome: str, user: UserSchema) -> List:
    """Filtra pessoas por nome"""
    pessoas = await models.Pessoa.filter(
        nome__icontains=nome, client_id=user.client_id
    ).all()
    pessoas_list = [pessoa for pessoa in pessoas]

    return pessoas_list


async def by_cpf_cnpj(cpf_cnpj: str, user: UserSchema) -> Union[models.Pessoa, None]:
    """Filtra pessoas ou empresas pelo cpf ou cnpj"""
    pessoa = await models.Pessoa.filter(
        cpf_cnpj=cpf_cnpj, client_id=user.client_id
    ).first()
    if not pessoa:
        return None
    return pessoa


async def find_principal(
    pk: str, user: UserSchema
) -> Union[schemas.PessoaResponseSchema, None]:
    """Filtra empresas e retorna sua principal"""
    empresa = await models.Pessoa.filter(suuid=pk, client_id=user.client_id).first()
    if not empresa:
        return None
    if empresa.matriz:
        return schemas.PessoaResponseSchema(**dict(empresa))
    return await find_principal(empresa.pessoa_suuid, user)


def _make_contato_response(
    contato: models.InfoContato,
) -> schemas.InfoContatoResponseSchema:
    contato_dict = dict(contato)
    contato_dict["id"] = contato.suuid
    contato_dict["pessoa_id"] = contato.pessoa_suuid
    return schemas.InfoContatoResponseSchema(**contato_dict)


async def save_contato(
    pk: str, payload: schemas.InfoContatoPayloadSchema, user: UserSchema
) -> Union[schemas.InfoContatoResponseSchema, None]:
    """Salva e atualiza informações de contato de uma pessoa"""
    attempt = 0
    while attempt < 3:
        attempt += 1
        try:
            if pk:
                info_contato = await models.InfoContato.filter(
                    suuid=pk, client_id=user.client_id
                ).first()
                if not info_contato:
                    return None
                info_contato.email = payload.email
                info_contato.telefone = payload.telefone
                info_contato.tipo = payload.tipo
                info_contato.created_at = datetime.fromisoformat(
                    str(info_contato.created_at)[:23]
                )  # milesimos
            else:
                info_contato = models.InfoContato(
                    client_id=user.client_id,
                    email=payload.email,
                    pessoa_suuid=payload.pessoa_id,
                    telefone=payload.telefone,
                    tipo=payload.tipo,
                    suuid=create_suuid(),
                )
            await info_contato.save()
            return _make_contato_response(info_contato)
        except Exception as err:
            logging.error(
                f"Falha na tentativa de salvar contato: {attempt}/3\n: {str(err)}"
            )
            await asyncio.sleep(attempt * 5)


async def get_contato(
    pk: str, user: UserSchema
) -> Union[schemas.InfoContatoResponseSchema, None]:
    """Retorna as informççoes de contato de uma pessoa por id"""
    info_contato = await models.InfoContato.filter(
        suuid=pk, client_id=user.client_id
    ).first()
    if not info_contato:
        return None
    return _make_contato_response(info_contato)


async def get_contato_all(
    pk: str, user: UserSchema
) -> Union[List[schemas.InfoContatoResponseSchema], None]:
    """Retorna todas os contatos vinculados a uma pessoa"""
    infos_contato = await models.InfoContato.filter(
        pessoa_suuid=pk, client_id=user.client_id
    ).all()
    if not infos_contato:
        return None
    return [_make_contato_response(info) for info in infos_contato]


async def delete_contato(pk: str, user: UserSchema) -> bool:
    """Apaga as informações de contato de uma pessoa por id"""
    info_contato = await models.InfoContato.filter(
        suuid=pk, client_id=user.client_id
    ).first()
    if not info_contato:
        return False
    result = await info_contato.delete()
    if result:
        return False
    return True


def validate_cpf_cnpj(pessoa: models.Pessoa) -> bool:
    """Filtra cpf ou cnpf e valida o número"""
    if pessoa.tipo == "FISICA":
        return validate_cpf(pessoa.cpf_cnpj)
    if pessoa.cadastro and len(pessoa.cadastro) > 5:  # TODO: criar regra
        return True
    return validate_cnpj(pessoa.cpf_cnpj)


def validate_cpf(cpf: str) -> bool:
    """Verifica se a string é um cpf válido"""
    try:
        if len(cpf) != 11:
            return False
        base = cpf[:9]
        dv = cpf[9:]
        same_digit = True
        for i, digit in enumerate(base):
            if i < len(base) - 1 and digit != base[i + 1]:
                same_digit = False
                break
        if same_digit:
            return False
        dv1_sum = 0
        for i in range(len(base)):
            dv1_sum += int(base[i]) * (10 - i)
        dv1_mod = dv1_sum % 11
        dv1 = str(11 - dv1_mod) if 11 - dv1_mod < 10 else "0"
        base2 = base + dv1
        dv2_sum = 0
        for i in range(len(base2)):
            dv2_sum += int(base2[i]) * (11 - i)
        dv2_mod = dv2_sum % 11
        dv2 = str(11 - dv2_mod) if 11 - dv2_mod < 10 else "0"
        return dv[0] == dv1 and dv[1] == dv2
    except (IndexError, ValueError):
        return False


def validate_cnpj(cnpj: str) -> bool:
    """Verifica se a string é um cnpj válido"""
    try:
        if len(cnpj) != 14:
            return False
        base = cnpj[:12]
        dv = cnpj[12:]
        # cada digito do cnpj tem um peso
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        dv1_sum = 0
        for i in range(len(weights)):
            dv1_sum += int(base[i]) * weights[i]
        dv1_mod = dv1_sum % 11
        dv1 = str(11 - dv1_mod) if 11 - dv1_mod < 10 else "0"
        # como mais um digito vai ser validado, eh incluido mais um peso a lista
        weights.insert(0, 6)  #
        base2 = base + dv1
        dv2_sum = 0
        for i in range(len(weights)):
            dv2_sum += int(base2[i]) * weights[i]
        dv2_mod = dv2_sum % 11
        dv2 = str(11 - dv2_mod) if 11 - dv2_mod < 10 else "0"
        return dv[0] == dv1 and dv[1] == dv2
    except (IndexError, ValueError):
        return False
