import os
from typing import List, Union

from fastapi import (APIRouter, Depends, File, HTTPException, Security,
                     UploadFile)
from openpyxl import load_workbook
from pydantic import ValidationError

from epona.auth import schemas as auth
from epona.auth.services import get_current_active_user

from . import schemas, services

router = APIRouter()


@router.post("", response_model=schemas.PessoaResponseSchema, status_code=201)
async def create(
    payload: schemas.PessoaPayloadSchema,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:create"]
    ),
) -> schemas.PessoaResponseSchema:
    try:
        pessoa_suuid = await services.save(payload, user)

        response_object = payload.model_dump()
        response_object["id"] = pessoa_suuid
        response_object["suuid"] = pessoa_suuid

        return schemas.PessoaResponseSchema(**response_object)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Erro desconhecido ao criar pessoa")


@router.put("", response_model=schemas.PessoaResponseSchema, status_code=201)
async def update(
    payload: schemas.PessoaPayloadSchema,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:update"]
    ),
) -> schemas.PessoaResponseSchema:
    pessoa_suuid = await services.update(payload, user)
    if not pessoa_suuid:
        raise HTTPException(status_code=401, detail="Não autorizado")
    response = payload.model_dump()
    response["id"] = pessoa_suuid
    response["suuid"] = pessoa_suuid
    return schemas.PessoaResponseSchema(**response)


@router.get("/{pk}", response_model=schemas.PessoaSchema)
async def read(
    pk: str,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["pessoas:read"]),
) -> schemas.PessoaSchema:
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não autenticado")
    pes = await services.get(pk, user)
    if not pes:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return pes


@router.get("/cpf_cnpj/{cpf_cnpj}", response_model=schemas.PessoaSchema)
async def cpf_cnpj(
    cpf_cnpj: str,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["pessoas:read"]),
) -> schemas.PessoaSchema:
    pes = await services.by_cpf_cnpj(cpf_cnpj, user)
    if not pes:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return dict(pes)


@router.get("", response_model=List[schemas.PessoaSchema])
async def read_all(
    user: auth.UserSchema = Security(get_current_active_user, scopes=["pessoas:read"])
) -> List[schemas.PessoaSchema]:
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não autenticado")
    return await services.get_all(user)


@router.delete("/{pk}", status_code=200)
async def delete(
    pk: str,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:delete"]
    ),
) -> dict:
    result = await services.delete(pk, user)
    if result:
        return {"detail": "Pessoa excluída"}
    raise HTTPException(status_code=400, detail="Pessoa não encontrada")


@router.get("/principal/{pk}", status_code=200)
async def find_principal(
    pk: str,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["pessoas:read"]),
) -> schemas.PessoaResponseSchema:
    principal = await services.find_principal(pk, user)
    if not principal:
        raise HTTPException(status_code=404, detail="Pessoa principal não encontrada")
    return principal


@router.post(
    "/xlsx", response_model=List[schemas.PessoaResponseSchema], status_code=201
)
async def process_file(
    upload: UploadFile = File(...),
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:create"]
    ),
) -> Union[List[schemas.PessoaResponseSchema], None]:
    if not upload:
        raise HTTPException(detail="Nenhum arquivo enviado", status_code=404)
    with open(f"{user.client_id}_{user.username}_tempfile.xlsx", "wb") as xlsx:
        contents = upload.file.read()
        xlsx.write(contents)
        wb = load_workbook(xlsx.name, read_only=True)
        try:
            result = await services.save_xlsx(wb, user)
        except (ValueError, ValidationError, Exception) as err:
            raise HTTPException(detail=str(err), status_code=422)
        finally:
            os.remove(xlsx.name)
        if result is None:
            raise HTTPException(
                detail="Falha na leitura dos dados. Comunique o administrador",
                status_code=404,
            )
        return result


@router.post(
    "/contato", response_model=schemas.InfoContatoResponseSchema, status_code=201
)
async def save_contato(
    payload: schemas.InfoContatoPayloadSchema,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:create"]
    ),
) -> schemas.InfoContatoResponseSchema:
    result = await services.save_contato("", payload, user)
    if not result:
        raise HTTPException(status_code=400, detail="Falhar ao salvar")
    return result


@router.delete("/contato/{pk}", response_model=bool)
async def delete_contato(
    pk: str,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:delete"]
    ),
) -> bool:
    result = await services.delete_contato(pk, user)
    if not result:
        raise HTTPException(status_code=404, detail="InfoContato não encontrada")
    return result


@router.put("/contato/{pk}", response_model=schemas.InfoContatoResponseSchema)
async def update_contato(
    pk: str,
    payload: schemas.InfoContatoPayloadSchema,
    user: auth.UserSchema = Security(
        get_current_active_user, scopes=["pessoas:delete"]
    ),
) -> schemas.InfoContatoResponseSchema:
    result = await services.save_contato(pk, payload, user)
    if not result:
        raise HTTPException(status_code=404, detail="InfoContato não encontrada")
    return result


@router.get("/contato/{pk}", response_model=schemas.InfoContatoResponseSchema)
async def get_contato(
    pk: str, user: auth.UserSchema = Depends(get_current_active_user)
) -> schemas.InfoContatoResponseSchema:
    result = await services.get_contato(pk, user=user)
    if not result:
        raise HTTPException(status_code=404, detail="InfoContato não encontrada")
    return result


@router.get("/contato/all/{pk}", response_model=List[schemas.InfoContatoResponseSchema])
async def get_contato_all(
    pk: str,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["pessoas:read"]),
) -> List[schemas.InfoContatoResponseSchema]:
    result = await services.get_contato_all(pk, user)
    if not result:
        raise HTTPException(
            status_code=404, detail="Nenhuma informação de contato encontrada"
        )
    return result
