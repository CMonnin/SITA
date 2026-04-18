import json

import pytest

from sita_web.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestMatrixEndpoint:
    def test_success(self, client):
        res = client.post(
            "/api/matrix",
            data=json.dumps({"formula": "C11H26NO2Si2", "backbone_c": 3}),
            content_type="application/json",
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "matrix" in data
        assert "csv" in data
        assert len(data["matrix"]) == 4  # backbone_c + 1

    def test_missing_formula(self, client):
        res = client.post(
            "/api/matrix",
            data=json.dumps({"backbone_c": 3}),
            content_type="application/json",
        )
        assert res.status_code == 400
        assert "formula" in res.get_json()["error"]

    def test_missing_backbone_c(self, client):
        res = client.post(
            "/api/matrix",
            data=json.dumps({"formula": "C3H7NO2"}),
            content_type="application/json",
        )
        assert res.status_code == 400
        assert "backbone_c" in res.get_json()["error"]

    def test_invalid_backbone_c(self, client):
        res = client.post(
            "/api/matrix",
            data=json.dumps({"formula": "C3H7NO2", "backbone_c": "abc"}),
            content_type="application/json",
        )
        assert res.status_code == 400
        assert "integer" in res.get_json()["error"]

    def test_backbone_c_exceeds_formula(self, client):
        res = client.post(
            "/api/matrix",
            data=json.dumps({"formula": "C3H7NO2", "backbone_c": 10}),
            content_type="application/json",
        )
        assert res.status_code == 400


class TestMdvStarEndpoint:
    def test_success(self, client):
        res = client.post(
            "/api/mdv-star",
            data=json.dumps({
                "formula": "C11H26NO2Si2",
                "backbone_c": 3,
                "mdv": "0.6228, 0.1517, 0.0749, 0.1507",
            }),
            content_type="application/json",
        )
        assert res.status_code == 200
        data = res.get_json()
        assert "mdv_star" in data
        assert "csv" in data
        assert len(data["mdv_star"]) == 4

    def test_missing_mdv(self, client):
        res = client.post(
            "/api/mdv-star",
            data=json.dumps({"formula": "C11H26NO2Si2", "backbone_c": 3}),
            content_type="application/json",
        )
        assert res.status_code == 400
        assert "mdv" in res.get_json()["error"]

    def test_missing_formula(self, client):
        res = client.post(
            "/api/mdv-star",
            data=json.dumps({"backbone_c": 3, "mdv": "0.5, 0.5"}),
            content_type="application/json",
        )
        assert res.status_code == 400


class TestIndexPage:
    def test_returns_html(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert b"SITA" in res.data
