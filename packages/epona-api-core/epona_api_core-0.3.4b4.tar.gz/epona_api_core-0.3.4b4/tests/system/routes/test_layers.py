from os.path import dirname


def test_save_geometry_point(test_app_with_db, access_token, monkeypatch):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    payload = {
        "id_entity": "a12345678-123",
        "entity_type": "unidade",
        "cords": {"type":"Point","coordinates":[-48.23456, 20.12345]},
        "geom_type": "ponto",
    }

    resp = test_app_with_db.post("/layers/save-geometry", json=payload, headers=headers)

    assert resp.status_code == 201


def test_get_geometrias(test_app_with_db, access_token, monkeypatch):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    payload = {
        "id_entity": "c12345678-123",
        "entity_type": "entidade",
    }

    test_app_with_db.post("/layers/save-geometry", json=payload, headers=headers)

    resp = test_app_with_db.post(
        "/layers/get-geometries", json=payload, headers=headers
    )

    assert resp.status_code == 200


def test_load_geometry_shapefile(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    base_path = dirname(dirname(dirname(__file__)))
    file_name = f"{base_path}/data/limite_area.zip"
    file = {"upload": open(file_name, "rb")}

    resp = test_app_with_db.post("/layers/load-geometry", files=file, headers=headers)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["geomType"] == "POLYGON"
    assert "geometry" in resp_data["cords"]


def test_save_geometry_shapefile(test_app_with_db, access_token):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    base_path = dirname(dirname(dirname(__file__)))
    file_name = f"{base_path}/data/limite_area.zip"
    file = {"upload": open(file_name, "rb")}

    resp = test_app_with_db.post("/layers/load-geometry", files=file, headers=headers)
    resp_data = resp.json()

    data = {
        "id_entity": "123456789-abc",
        "entity_type": "area",
        "cords": resp_data["cords"]["geometry"],
        "representation": "LIMITE",
        "geom_type": "POLYGON",
        "zoom": 14
    }
    resp = test_app_with_db.post("/layers/save-geometry", json=data, headers=headers)
    assert resp.status_code == 201
    assert resp.json() == "INSERT 0 1"
