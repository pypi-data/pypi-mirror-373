import json
import random

import jwt
import pytest
from jwt.exceptions import InvalidTokenError

from epona.auth import services
from epona.auth.schemas import EmailPayload


def test_register(test_app_with_db, access_token):
    form_data = {
        "id": 1,
        "active": "true",
        "client_id": "test_client",
        "email": "usuario@email.com",
        "username": "usuario",
        "password": "senha",
        "scope": "user",
        "sector": 2,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = test_app_with_db.post("/auth/register", data=form_data, headers=headers)
    assert resp.status_code == 200
    token = resp.json()
    assert token["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    resp = test_app_with_db.delete("/auth/users/usuario", headers=headers)
    assert resp.status_code == 200


def test_auth_login(test_app_with_db, normal_user):
    form_data = {
        "username": "normal_user",
        "password": "normal",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    assert resp.status_code == 200


def test_auth_invalid_user(test_app_with_db):
    form_data = {
        "username": "inexisting",
        "password": "senha",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    assert resp.status_code == 400


def test_auth_wrong_password(test_app_with_db, normal_user):
    form_data = {
        "username": "normal_user",
        "password": "wrong",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    assert resp.status_code == 400


def test_auth_users_me(test_app_with_db, normal_user):
    form_data = {
        "username": "normal_user",
        "password": "normal",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    assert resp.status_code == 200

    token = resp.json()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token['access_token']}",
    }
    resp = test_app_with_db.get("/auth/users/me", headers=headers)
    assert resp.status_code == 200


def test_auth_get_current_user(test_app_with_db, normal_user):
    form_data = {
        "username": "normal_user",
        "password": "normal",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    assert resp.status_code == 200
    token = resp.json()

    resp = test_app_with_db.get(f"/auth/users/get-current/{token['access_token']}")
    assert resp.status_code == 200
    assert resp.json()["username"] == "normal_user"


def test_auth_delete_user(test_app_with_db, access_token, deleted_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    resp = test_app_with_db.delete("/auth/users/deleted_user", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is True


def test_user_permission_add(test_app_with_db, access_token, another_user):
    permissions = {
        "client_id": "test_client",
        "entities": ["all"],
        "permissions": [
            "pessoas:create",
            "users:read",
        ],
        "username": "another_user",
    }

    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    resp = test_app_with_db.post(
        "/auth/users/permission", json=permissions, headers=headers
    )
    assert resp.status_code == 201
    assert resp.json() == 2


def test_check_user_permissions(test_app_with_db, access_token, normal_user):
    user = {"username": "normal_user", "password": "normal", "client_id": "test_client"}
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    resp = test_app_with_db.post("/auth/login", data=user, headers=headers)

    assert resp.status_code == 200
    token = resp.json()
    token = jwt.decode(
        token["access_token"], services.SECRET_KEY, algorithms=[services.ALGORITHM]
    )
    assert len(token["scopes"].split()) == 2
    assert "pessoas:create" in token["scopes"]


def test_add_permission(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    permission = {
        "name": f"nova:read {str(random.random())}",
        "description": "Ler novas entidades",
    }
    resp = test_app_with_db.post("/auth/permission", json=permission, headers=headers)
    assert resp.status_code == 201
    assert resp.json() is True


def test_get_users(test_app_with_db, access_token, another_user, normal_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    resp = test_app_with_db.get("/auth/users", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3  # 3 chamados aqui


def test_get_user_detail(test_app_with_db, access_token, normal_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "applications/json"}

    resp = test_app_with_db.get("/auth/users/normal_user", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "normal_user"


def test_get_user_detail_with_permissions(test_app_with_db, access_token, normal_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "applications/json"}

    permissions = {
        "client_id": "test_client",
        "entities": ["all"],
        "permissions": [
            "users:read",
            "users:create",
            "users:update",
        ],
        "username": "normal_user",
    }

    test_app_with_db.post("/auth/users/permission", json=permissions, headers=headers)

    resp = test_app_with_db.get("/auth/users/normal_user", headers=headers)
    assert resp.status_code == 200
    user = resp.json()
    assert user["username"] == "normal_user"
    assert len(user["permissions"]) >= 3


def test_update_user_using_admin(test_app_with_db, access_token, normal_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    normal_user = jwt.decode(
        normal_user, services.SECRET_KEY, algorithms=[services.ALGORITHM]
    )
    assert "normal_user" in normal_user["sub"]
    assert normal_user["scopes"] == "user pessoas:create"
    user = {
        "active": False,
        "client_id": "test_client",
        "scope": "admin",
        "username": "normal_user",
        "password": "-",
        "email": "-",
    }

    resp = test_app_with_db.put("/auth/users", data=user, headers=headers)

    assert resp.status_code == 200
    assert resp.json()["active"] is False
    assert resp.json()["scope"] == "admin"


def test_auth_get_permissions(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    resp = test_app_with_db.get("/auth/permissions", headers=headers)
    assert resp.status_code == 200
    permissions = resp.json()
    assert len(permissions) >= 8  # 8 permissons api 1 permissão teste


@pytest.mark.xfail
def test_auth_delete_user_permissions(test_app_with_db, access_token, another_user):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    permissions = {
        "client_id": "test_client",
        "entities": ["all"],
        "permissions": [
            "users:create",
            "users:read",
            "users:delete",
            "users:update",
        ],
        "username": "another_user",
    }
    test_app_with_db.post("/auth/users/permission", json=permissions, headers=headers)

    payload = {
        "client_id": "test_client",
        "entities": ["all"],
        "username": "another_user",
        "permissions": ["users:create", "users:delete"],
    }
    resp = test_app_with_db.delete(
        "/auth/users/user-permission", json=payload, headers=headers
    )

    assert resp.status_code == 200
    assert resp.json() == 2


def test_send_email(monkeypatch):
    def send_email_mock(*args, **kwargs):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    monkeypatch.setattr(services, "send_email", send_email_mock)
    # email
    payload = {
        "sender": "Sigeli Epona <sigeli@eponaconsultoria.com.br>",
        "recipient": "test@email.com",
        "subject": "Sigeli email test",
        "body_text": "Hello,\n\nPlease see this test email",
        "html_text": """\
            <html>
            <head></head>
            <body>
            <h1>Hello!</h1>
            <p>Please see this email test from Epona Consultoria.</p>
            </body>
            </html>
            """,
        "charset": "utf-8",
    }
    resp = services.send_email(EmailPayload(**payload))
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200


@pytest.mark.xfail
def test_password_recover(test_app_with_db, normal_user, monkeypatch):
    def send_email_mock(*args, **kwargs):
        return {"MessageId": "1"}

    monkeypatch.setattr(services, "send_email", send_email_mock)

    data = {"email": "normal@email.com", "client_id": "test_client"}
    resp = test_app_with_db.post("/auth/password-recover", json=data)
    assert resp.status_code == 200
    assert resp.json()["msg"] == "E-mail de recuperação enviado com sucesso"


def test_recovering(test_app_with_db, normal_user, monkeypatch):
    def jwt_decode_mock(*args, **kwargs):
        return {"email": "normal@email.com"}

    monkeypatch.setattr(services.jwt, "decode", jwt_decode_mock)

    data = {
        "client_id": "test_client",
        "password": "_senha_",
        "password_confirm": "_senha_",
        "username": "normal_user",
        "token": "token-str",
    }
    resp = test_app_with_db.post("/auth/recovering", data=data)
    assert resp.status_code == 200
    assert resp.json()["msg"] == "Senha alterada com sucesso"


def test_recovering_invalid_email(test_app_with_db, normal_user, monkeypatch):
    def jwt_decode_mock(*args, **kwargs):
        return {"email": "another-email@test.com"}

    monkeypatch.setattr(services.jwt, "decode", jwt_decode_mock)

    data = {
        "client_id": "test_client",
        "password": "_senha_",
        "password_confirm": "_senha_",
        "username": "normal_user",
        "token": "token-str",
    }
    resp = test_app_with_db.post("/auth/recovering", data=data)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Usuário não encontrado"


def test_recovering_invalid_token(test_app_with_db, normal_user, monkeypatch):
    def jwt_decode_mock(*args, **kwargs):
        raise InvalidTokenError("token")

    monkeypatch.setattr(services.jwt, "decode", jwt_decode_mock)

    data = {
        "client_id": "test_client",
        "password": "_senha_",
        "password_confirm": "_senha_",
        "username": "normal_user",
        "token": "token-str",
    }
    resp = test_app_with_db.post("/auth/recovering", data=data)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token inválido"


def test_password_change(test_app_with_db, another_user, monkeypatch):
    headers = {"Authorization": f"Bearer {another_user}", "accept": "application/json"}
    data = {
        "client_id": "test_client",
        "password": "_senha_",
        "password_confirm": "_senha_",
        "username": "another_user",
        "token": another_user,
    }
    resp = test_app_with_db.post("/auth/password-change", data=data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["msg"] == "Senha alterada com sucesso"
