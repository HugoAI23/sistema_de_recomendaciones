from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["zero_cost_mode"] is True
    assert "Fase 4" in data["phase_completed"]


def test_get_teams_endpoint():
    response = client.get("/api/v1/teams")
    assert response.status_code == 200
    teams = response.json()
    assert len(teams) == 20
    assert any(t["name"] == "Arsenal" for t in teams)


def test_get_fixtures_endpoint():
    response = client.get("/api/v1/fixtures?gameweek=29")
    assert response.status_code == 200
    fixtures = response.json()
    assert len(fixtures) == 10


def test_get_fixtures_gameweek_6_endpoint():
    response = client.get("/api/v1/fixtures?gameweek=6")
    assert response.status_code == 200
    fixtures = response.json()
    assert len(fixtures) == 10
    for f in fixtures:
        assert f["gameweek"] == 6


def test_recommendations_gameweek_6_top3():
    payload = {
        "gameweek": 6,
        "profile": "cv_optimal",
        "top_n": 3
    }
    response = client.post("/api/v1/recommendations/top3", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gameweek"] == 6
    assert len(data["top_matches"]) == 3
    assert data["top_matches"][0]["excitement_score"] > 0
    assert len(data["top_matches"][0]["reasons"]) > 0


def test_recommendations_gameweek_6_ml_hybrid():
    response = client.get("/api/v1/recommendations/top3?gameweek=6&profile=cv_optimal&model_type=ml_hybrid&top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert data["gameweek"] == 6
    assert data["scoring_mode"] == "ml_hybrid"
    assert len(data["top_matches"]) == 3
    assert data["top_matches"][0]["excitement_score"] > 0


def test_get_fixtures_gameweek_8_endpoint():
    response = client.get("/api/v1/fixtures?gameweek=8")
    assert response.status_code == 200
    fixtures = response.json()
    assert len(fixtures) == 10
    for f in fixtures:
        assert f["gameweek"] == 8


def test_recommendations_gameweek_8_top3():
    payload = {
        "gameweek": 8,
        "profile": "cv_optimal",
        "top_n": 3
    }
    response = client.post("/api/v1/recommendations/top3", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gameweek"] == 8
    assert len(data["top_matches"]) == 3
    assert data["top_matches"][0]["excitement_score"] > 0
    assert len(data["top_matches"][0]["reasons"]) > 0


def test_recommendations_gameweek_8_ml_hybrid():
    response = client.get("/api/v1/recommendations/top3?gameweek=8&profile=cv_optimal&model_type=ml_hybrid&top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert data["gameweek"] == 8
    assert data["scoring_mode"] == "ml_hybrid"
    assert len(data["top_matches"]) == 3
    assert data["top_matches"][0]["excitement_score"] > 0


def test_get_fixtures_with_date_filter():
    response = client.get("/api/v1/fixtures?date=2026-03-31")
    assert response.status_code == 200
    fixtures = response.json()
    assert len(fixtures) == 2
    for f in fixtures:
        assert f["kickoff_time"].startswith("2026-03-31")


def test_recommendations_top3_post():
    payload = {
        "gameweek": 29,
        "profile": "balanced",
        "top_n": 3
    }
    response = client.post("/api/v1/recommendations/top3", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["gameweek"] == 29
    assert data["profile_used"] == "balanced"
    assert len(data["top_matches"]) == 3

    first_match = data["top_matches"][0]
    assert "excitement_score" in first_match
    assert "reasons" in first_match
    assert len(first_match["reasons"]) > 0


def test_recommendations_top3_get():
    response = client.get("/api/v1/recommendations/top3?gameweek=29&profile=cv_optimal&top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert data["gameweek"] == 29
    assert data["profile_used"] == "cv_optimal"
    assert len(data["top_matches"]) == 3
    assert data["top_matches"][0]["excitement_score"] > 0


def test_recommendations_with_date_filter():
    # Probar filtro por fecha en POST
    payload = {
        "date": "2026-03-31",
        "profile": "cv_optimal",
        "top_n": 5
    }
    response = client.post("/api/v1/recommendations/top3", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["date_filter"] == "2026-03-31"
    assert data["total_evaluated_matches"] == 2
    assert len(data["top_matches"]) == 2
    for match in data["top_matches"]:
        assert match["fixture"]["kickoff_time"].startswith("2026-03-31")

    # Probar filtro por fecha en GET
    res_get = client.get("/api/v1/recommendations/top3?date=2026-03-31&profile=cv_optimal")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["date_filter"] == "2026-03-31"
    assert get_data["total_evaluated_matches"] == 2


def test_dashboard_endpoints_html():
    # Probar endpoint raíz
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "text/html" in res_root.headers["content-type"]
    assert "Premier League" in res_root.text

    # Probar /dashboard
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "text/html" in res_dash.headers["content-type"]
    assert "RECOMENDAR PARTIDOS" in res_dash.text

    # Probar /api/v1/dashboard
    res_api_dash = client.get("/api/v1/dashboard")
    assert res_api_dash.status_code == 200
    assert "text/html" in res_api_dash.headers["content-type"]


def test_fixture_analysis_endpoint():
    response = client.get("/api/v1/fixtures/101/analysis?profile=balanced")
    assert response.status_code == 200
    data = response.json()
    assert data["fixture"]["id"] == 101
    assert "numerical_features" in data
    assert "nlp_features" in data
    assert "excitement_score" in data
