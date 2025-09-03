def test_health_check(test_app):
    resp = test_app.get("/ping/health-check")
    assert resp.status_code == 200
