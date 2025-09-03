from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from epona.auth import schemas, services
from epona.settings import TOKEN_DURATION

ACCESS_TOKEN_EXPIRE_MINUTES = TOKEN_DURATION
router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = await services.authenticate_user(
        form_data.username, form_data.password, form_data.client_id
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Usuário ou senha incorreto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.create_access_token(
        data={"sub": f"{form_data.client_id}:{user.username}", "scopes": user.scope},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.Token)
async def register(
    form_data: schemas.UserForm = Depends(schemas.UserForm.as_form),
) -> dict:
    http_exception = HTTPException(
        status_code=400,
        detail=(
            "Nao foi possível criar o usuário. Verifique se o e-mail e o CPF são "
            "únicos na empresa, se o nome escolhido para empresa está disponível "
            "ou e se o domínio do e-mail pode ser vinculado à empresa."
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not form_data.password or not form_data.email:
        raise http_exception
    user_dict = form_data.model_dump()
    hashed_password = services.get_password_hash(form_data.password)
    user_dict["password_hash"] = hashed_password
    user_dict.pop("password", None)
    user_dict["id"] = 1

    user = schemas.UserSchema(**user_dict)
    user_wp = await services.save(user)
    if not user_wp:
        raise http_exception
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.create_access_token(
        data={"sub": f"{user.client_id}:{user_wp.username}", "scopes": user_wp.scope},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(
    current_user: schemas.UserSchema = Depends(services.get_current_active_user),
) -> schemas.UserSchema:
    return current_user


@router.get("/users/{username}", response_model=schemas.UserPermissionResponseSchema)
async def get_user_detail(
    username: str,
    user: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin"]
    ),
) -> Optional[schemas.UserPermissionResponseSchema]:
    try:
        user = await services.get_user_detail(username, user)
        return user
    except (HTTPException, Exception):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {username} inexistente",
        )


@router.get("/users", response_model=List[schemas.UserSchema])
async def get_users(
    user: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin"]
    )
) -> Optional[List[schemas.UserSchema]]:
    try:
        return await services.get_users(user)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum usuário encontrado"
        )


@router.delete("/users/user-permission", response_model=int)
async def delete_user_permission(
    payload: schemas.UserPermissionPayloadSchema,
    _: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin"]
    ),
) -> int:
    return await services.delete_user_permission(payload)


@router.delete("/users/{username}", response_model=bool)
async def delete_user(
    username: str,
    user: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin", "users:delete"]
    ),
) -> bool:
    try:
        return await services.delete(username, user)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {username} não encontrado",
        )


@router.put("/users", response_model=schemas.UserForm, status_code=200)
async def update_user(
    payload: schemas.UserForm = Depends(schemas.UserForm.as_form),
    user: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin", "users:update"]
    ),
) -> schemas.UserSchema:
    try:
        return await services.update(payload, user)
    except HTTPException:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Usuário {payload.username} não encontrado"
        )


@router.get("/users/get-current/{token}")
async def get_current_user(token: str):
    security_scopes = Security()
    return await services.get_current_user(security_scopes, token)


@router.post("/users/permission", response_model=int, status_code=201)
async def user_add_permission(
    payload: schemas.UserPermissionPayloadSchema,
    user: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["admin"]
    ),
) -> int:
    return await services.user_add_permission(payload, user)


@router.post("/permission", response_model=bool, status_code=201)
async def add_permission(
    payload: schemas.PermissionSchema,
    _: schemas.UserSchema = Security(
        services.get_current_active_user, scopes=["super-admin"]
    ),
):
    try:
        return await services.add_permission(payload)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Não foi possível incluir a permissão",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail="Não foi possível atribuir a permissão aos usuários admin",
        )


@router.get("/permissions", response_model=List[schemas.PermissionSchema])
async def get_permissions(
    _: schemas.UserSchema = Security(services.get_current_active_user, scopes=["admin"])
) -> Optional[List[schemas.PermissionSchema]]:
    return await services.get_permissions()


@router.post("/password-recover", response_model=Optional[schemas.EmailResponse])
async def password_recover(
    payload: schemas.PasswordRecoverPayload,
) -> Optional[schemas.EmailResponse]:
    return await services.password_recover(payload, "./password.html")


@router.post("/recovering", response_model=Optional[schemas.EmailResponse])
async def recovering(
    form_data: schemas.ChangePassword = Depends(schemas.ChangePassword.as_form),
) -> Optional[schemas.EmailResponse]:
    result = await services.recovering(form_data)
    if not result:
        raise HTTPException(401, "Token inválido")
    return result


@router.post("/password-change", response_model=Optional[schemas.EmailResponse])
async def password_change(
    form_data: schemas.ChangePassword = Depends(schemas.ChangePassword.as_form),
    user: schemas.UserSchema = Depends(services.get_current_active_user),
) -> Optional[schemas.EmailResponse]:
    result = await services.change_password(form_data, user)
    return result
