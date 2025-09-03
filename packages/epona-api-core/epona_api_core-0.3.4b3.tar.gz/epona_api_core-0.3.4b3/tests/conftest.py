import asyncio

import pytest
from starlette.testclient import TestClient
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

from app.config import Settings, get_settings
from app.db import models
from app.main import create_application

settings: Settings = get_settings()


def get_settings_override():
    return Settings(testing=1, database_url=settings.database_url)


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        yield test_client

    # tear down


@pytest.fixture(scope="session")
def test_app_with_db():
    # set up
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    register_tortoise(
        app=app,
        db_url=get_settings().database_url,
        modules={"models": models},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down
    url = get_settings().database_url

    run_async(Tortoise.init(db_url=url, modules={"models": models}))
    conn = Tortoise.get_connection("default")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(conn.execute_query("truncate users cascade"))
    loop.run_until_complete(
        conn.execute_query("delete from clients where name='test_client'"))
    loop.run_until_complete(conn.execute_query(
        "delete from permissions where description='Ler novas entidades'"))
    loop.run_until_complete(conn.execute_query("truncate table geometries;"))


@pytest.fixture(scope="session")
def access_token(test_app_with_db):
    user_data = {
        "id": 0,
        "active": "true",
        "client_id": "test_client",
        "email": "test@email.com",
        "username": "admin_user",
        "password": "admin_pass",
        "scope": "admin",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = test_app_with_db.post("/auth/register", data=user_data, headers=headers)
    yield resp.json()["access_token"]


@pytest.fixture(scope="module")
def normal_user(test_app_with_db, access_token):
    user_data = {
        "id": 0,
        "active": "true",
        "client_id": "test_client",
        "email": "normal@email.com",
        "username": "normal_user",
        "password": "normal",
        "scope": "user",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    test_app_with_db.post("/auth/register", data=user_data, headers=headers)

    user = {
        "active": True,
        "client_id": "test_client",
        "scope": "user",
        "username": "normal_user",
        "password": "-",
        "email": "-",
    }
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    test_app_with_db.put("/auth/users", data=user, headers=headers)

    form_data = {
        "username": "normal_user",
        "password": "normal",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)
    yield resp.json()["access_token"]


@pytest.fixture(scope="module")
def another_user(test_app_with_db, access_token):
    user_data = {
        "id": 0,
        "active": "true",
        "client_id": "test_client",
        "email": "another@email.com",
        "username": "another_user",
        "password": "another",
        "scope": "user",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    test_app_with_db.post("/auth/register", data=user_data, headers=headers)

    user = {
        "active": True,
        "client_id": "test_client",
        "scope": "user",
        "username": "another_user",
        "password": "-",
        "email": "-",
    }
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    resp = test_app_with_db.put("/auth/users", data=user, headers=headers)
    assert resp.status_code == 200
    form_data = {
        "username": "another_user",
        "password": "another",
        "client_id": "test_client",
    }
    resp = test_app_with_db.post("/auth/login", data=form_data)

    yield resp.json()["access_token"]


@pytest.fixture(scope="module")
def deleted_user(test_app_with_db):
    user_data = {
        "id": 0,
        "active": "true",
        "client_id": "test_client",
        "email": "deleted@email.com",
        "username": "deleted_user",
        "password": "deleted",
        "scope": "user",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = test_app_with_db.post("/auth/register", data=user_data, headers=headers)
    yield resp.json()["access_token"]


@pytest.fixture(scope="module")
def pessoa_contato(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {
        "nome": "Fulano de Tal",
        "cpf_cnpj": "00011122201",
        "tipo": "FISICA",
    }
    resp = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    return resp.json()
