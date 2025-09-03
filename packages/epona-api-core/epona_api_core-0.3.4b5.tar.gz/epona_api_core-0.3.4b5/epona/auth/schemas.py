from typing import List, Optional

from fastapi import Form
from pydantic import BaseModel

from .models import User


def hash_user(self: User):
    return hash(f"{self.client_id}{self.username}")


class UserSchema(BaseModel):
    id: int
    active: bool
    client_id: str
    email: str
    scope: str = ""
    sector: int = 1
    username: str
    password_hash: str
    permissions: List = []


UserSchema.__hash__ = hash_user


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class UserForm(BaseModel):
    active: bool = True
    client_id: Optional[str] = None
    email: str
    scope: Optional[str] = ""
    sector: Optional[int] = 1
    password: str
    username: str

    @classmethod
    def as_form(
        cls,
        active: bool = Form(...),
        client_id: str = Form(...),
        email: str = Form(...),
        scope: Optional[str] = Form(...),
        sector: Optional[int] = Form(1),
        password: str = Form(...),
        username: str = Form(...),
    ):
        return cls(
            active=active,
            client_id=client_id,
            email=email,
            scope=scope,
            sector=sector,
            password=password,
            username=username,
        )


class PermissionSchema(BaseModel):
    id: Optional[int] = 0
    name: str
    description: str


class UserPermissionPayloadSchema(BaseModel):
    client_id: str
    entities: List[str]
    permissions: List[str]
    username: str


class PermissionResponseSchema(UserPermissionPayloadSchema):
    id: int


class UserPermissionSchema(BaseModel):
    client_id: str
    description: str
    entities: str
    name: str
    permission_id: int
    user_id: int


class UserPermissionResponseSchema(BaseModel):
    id: int
    client_id: str
    permissions: List[UserPermissionSchema]
    username: str


class ChangePassword(BaseModel):
    client_id: str
    password: str
    password_confirm: str
    username: str
    token: Optional[str]

    @classmethod
    def as_form(
        cls,
        client_id: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        username: str = Form(...),
        token: str = Form(...),
    ) -> Form:
        return cls(
            client_id=client_id,
            password=password,
            password_confirm=password_confirm,
            username=username,
            token=token,
        )


class PasswordRecoverPayload(BaseModel):
    email: str
    client_id: str


class EmailPayload(BaseModel):
    sender: str
    recipient: str
    subject: str
    body_text: str
    html_text: Optional[str]
    charset: str


class EmailResponse(BaseModel):
    msg: str
    status: str
