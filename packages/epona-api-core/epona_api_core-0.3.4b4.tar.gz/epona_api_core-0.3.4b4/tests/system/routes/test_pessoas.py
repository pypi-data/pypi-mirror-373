import json
import os
from collections import namedtuple
from pathlib import Path

import pytest

from epona.pessoas.services import validate_cpf_cnpj


def test_create_pessoa(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    pessoa = {"nome": "Fulano de Tal", "cpf_cnpj": "00011122201", "tipo": "FISICA"}
    response = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)

    assert response.status_code == 201
    assert response.json()["nome"] == "Fulano de Tal"


def test_create_pessoa_invalid_json(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    pessoa = {}
    response = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)

    assert response.status_code == 422
    error_dict = {
        "detail": [
            {
                "loc": ["body", "cpf_cnpj"],
                "msg": "Field required",
                "type": "missing",
                "input": {},
            },
            {
                "loc": ["body", "nome"],
                "msg": "Field required",
                "type": "missing",
                "input": {},
            },
            {
                "loc": ["body", "tipo"],
                "msg": "Field required",
                "type": "missing",
                "input": {},
            },
        ]
    }
    assert response.json() == error_dict


def test_read_pessoa(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {"nome": "Fulano de Tal", "cpf_cnpj": "00011122203", "tipo": "FISICA"}
    response = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    pessoa_suuid = response.json()["suuid"]

    response = test_app_with_db.get(f"/pessoas/{pessoa_suuid}", headers=headers)
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["suuid"] == pessoa_suuid
    assert response_dict["nome"] == "Fulano de Tal"
    assert response_dict["cpf_cnpj"] == "00011122203"
    assert response_dict["tipo"] == "FISICA"


def test_read_pessoa_incorrect_id(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    response = test_app_with_db.get("/pessoas/999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa não encontrada"


def test_read_all_pessoas(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {"nome": "Beltrano de Tal", "cpf_cnpj": "00011122205", "tipo": "FISICA"}
    response = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    pessoa_suuid = response.json()["suuid"]

    response = test_app_with_db.get("/pessoas", headers=headers)
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["suuid"] == pessoa_suuid, response_list))) == 1


def test_delete_pessoa(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {"nome": "Beltrano de Tal", "cpf_cnpj": "00011122206", "tipo": "FISICA"}
    resp = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["cpf_cnpj"] == "00011122206"

    response = test_app_with_db.delete(
        f"/pessoas/{resp.json()['suuid']}", headers=headers
    )
    assert response.status_code == 200

    response = test_app_with_db.get(f"/pessoas/{resp.json()['suuid']}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa não encontrada"


def test_update_pessoa(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {"nome": "Beltrano de Tal 7", "cpf_cnpj": "00011122207", "tipo": "FISICA"}
    resp = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    assert resp.status_code == 201

    pessoa = resp.json()
    pessoa["nome"] = "Beltrano de Tal Alterado"
    resp = test_app_with_db.put("/pessoas", json=pessoa, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["nome"] == "Beltrano de Tal Alterado"

    response = test_app_with_db.delete(
        f"/pessoas/{resp.json()['suuid']}", headers=headers
    )
    assert response.status_code == 200

    response = test_app_with_db.get(f"/pessoas/{resp.json()['suuid']}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Pessoa não encontrada"


def test_delete_pessoa_unauthenticated_user(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa = {"nome": "Beltrano de Tal", "cpf_cnpj": "00011122206", "tipo": "FISICA"}
    resp = test_app_with_db.post("/pessoas", json=pessoa, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["cpf_cnpj"] == "00011122206"

    response = test_app_with_db.delete(f"/pessoas/{resp.json()['suuid']}")
    assert response.status_code == 401


base_path = Path(os.path.dirname(__file__))
base_path = base_path.parents[1]


def test_post_pessoas_xlsx(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    file = {"upload": open(base_path / "data/pessoas.xlsx", "rb")}

    response = test_app_with_db.post("/pessoas/xlsx", files=file, headers=headers)

    assert response.status_code == 201


def test_post_pessoas_xlsx_err_coluna(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    file = {"upload": open(base_path / "data/pessoas_err_coluna.xlsx", "rb")}

    response = test_app_with_db.post("/pessoas/xlsx", files=file, headers=headers)

    assert response.status_code == 422
    assert "Número de colunas na planilha" in response.json()["detail"]


def test_post_pessoas_xlsx_err_valor(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    file = {"upload": open(base_path / "data/pessoas_err_valor.xlsx", "rb")}

    response = test_app_with_db.post("/pessoas/xlsx", files=file, headers=headers)

    assert response.status_code == 422
    assert "Erro na linha 3. Verifique se " in response.json()["detail"]


def test_post_contato(test_app_with_db, access_token, pessoa_contato):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa_suuid = pessoa_contato["suuid"]

    contatos = [
        {
            "email": "normaluser@email.com",
            "pessoa_id": pessoa_suuid,
            "telefone": "123456789",
        },
        {
            "pessoa_id": pessoa_suuid,
            "telefone": "0987654321",
        },
    ]
    for contato in contatos:
        resp = test_app_with_db.post("/pessoas/contato", json=contato, headers=headers)
        assert resp.status_code == 201


def test_update_contato(test_app_with_db, access_token, pessoa_contato):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa_suuid = pessoa_contato["suuid"]

    resp = test_app_with_db.get(f"/pessoas/contato/all/{pessoa_suuid}", headers=headers)
    assert resp.status_code == 200
    contato_id = resp.json()[0]["suuid"]

    contato = {
        "email": "novocontato@email.com",
        "pessoa_id": pessoa_suuid,
    }
    resp = test_app_with_db.put(
        f"/pessoas/contato/{contato_id}", json=contato, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "novocontato@email.com"


def test_delete_contato(test_app_with_db, access_token, pessoa_contato):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    pessoa_suuid = pessoa_contato["suuid"]

    resp = test_app_with_db.get(f"/pessoas/contato/all/{pessoa_suuid}", headers=headers)
    assert resp.status_code == 200

    for contato in resp.json():
        resp = test_app_with_db.delete(
            f"/pessoas/contato/{contato['suuid']}", headers=headers
        )
        assert resp.status_code == 200
        assert resp.json() is True


Pessoa = namedtuple("Pessoa", "tipo cpf_cnpj, cadastro")


@pytest.mark.parametrize(
    "pessoa, result",
    [
        (Pessoa("FISICA", "123456789", ""), False),
        (Pessoa("FISICA", "12345678900", ""), False),
        (Pessoa("FISICA", "12345678909", ""), True),
        (Pessoa("FISICA", "14538220620", ""), True),
        (Pessoa("JURIDICA", "15104490002601", ""), False),
        (Pessoa("JURIDICA", "15104490002600", ""), True),
    ],
)
def test_validate_cpf_cnpj(pessoa, result):
    assert validate_cpf_cnpj(pessoa) == result
