import pytest
from fastapi.testclient import TestClient
from src.core.schemas import Team, Fixture, RecommendationRequest
from src.features.numerical import NumericalFeatureExtractor
from src.features.nlp import NLPFeatureExtractor
from src.engine.hybrid_model import CrossValidationWeightOptimizer, HybridMLScorer, compute_ndcg_at_k
from src.engine.scorer import MatchScorer
from src.data_ingestion.local_provider import LocalDataProvider
from src.api.app import app


def _create_sample_teams():
    city = Team(
        id=3, name="Manchester City", short_name="MCI", position=3, points=63, played=28,
        xg_for_last5=2.40, xga_for_last5=0.85, form="WDWWW", key_players_ict=340.0
    )
    arsenal = Team(
        id=1, name="Arsenal", short_name="ARS", position=1, points=64, played=28,
        xg_for_last5=2.45, xga_for_last5=0.65, form="WWWWW", key_players_ict=310.5
    )
    sheffield = Team(
        id=20, name="Sheffield United", short_name="SHU", position=20, points=14, played=28,
        xg_for_last5=0.85, xga_for_last5=2.50, form="DLLLL", key_players_ict=110.0
    )
    return city, arsenal, sheffield


def test_ndcg_at_k_computation():
    import numpy as np
    y_true = np.array([90.0, 80.0, 70.0, 60.0])
    y_pred_perfect = np.array([89.0, 79.0, 69.0, 59.0])
    y_pred_reversed = np.array([50.0, 60.0, 70.0, 80.0])

    ndcg_perfect = compute_ndcg_at_k(y_true, y_pred_perfect, k=3)
    ndcg_reversed = compute_ndcg_at_k(y_true, y_pred_reversed, k=3)

    assert ndcg_perfect == 1.0
    assert 0.0 <= ndcg_reversed < ndcg_perfect


def test_cross_validation_weight_optimizer():
    optimizer = CrossValidationWeightOptimizer(k_folds=5, random_state=42)
    cv_res = optimizer.optimize_weights_cv()

    assert cv_res.k_folds == 5
    assert cv_res.benchmark_matches_count >= 30
    assert cv_res.status == "validated"
    assert cv_res.spearman_rank_correlation > 0.60
    assert cv_res.ndcg_at_3 > 0.75
    assert cv_res.mean_squared_error > 0.0

    # Los pesos optimizados deben sumar exactamente 1.0
    w = cv_res.optimal_weights
    assert w.validate_weights() is True
    assert 0.15 <= w.w_xg <= 0.55
    assert 0.10 <= w.w_parity <= 0.45


def test_tactical_clash_operational_style():
    city, arsenal, sheffield = _create_sample_teams()
    extractor = NumericalFeatureExtractor()

    # Duelo ofensivo: City vs Arsenal
    fix_offensive = Fixture(id=1, gameweek=29, home_team=city, away_team=arsenal, kickoff_time="2026-03-31T15:30:00Z")
    feat_offensive = extractor.extract(fix_offensive)

    assert "Ataque vs Ataque" in feat_offensive.tactical_style_label
    assert feat_offensive.tactical_clash_intensity >= 0.70
    assert feat_offensive.progressive_passes_combined > 80.0
    assert feat_offensive.defensive_pressures_combined > 200.0

    # Choque asimétrico: City vs Sheffield United
    fix_asymmetric = Fixture(id=2, gameweek=29, home_team=city, away_team=sheffield, kickoff_time="2026-03-31T15:30:00Z")
    feat_asymmetric = extractor.extract(fix_asymmetric)

    assert "Asedio" in feat_asymmetric.tactical_style_label or "Contraataque" in feat_asymmetric.tactical_style_label
    assert feat_asymmetric.table_parity < 0.20


def test_hybrid_ml_scorer_training_and_prediction():
    city, arsenal, sheffield = _create_sample_teams()
    num_ext = NumericalFeatureExtractor()
    nlp_ext = NLPFeatureExtractor()

    fix_top = Fixture(id=101, gameweek=29, home_team=city, away_team=arsenal, kickoff_time="2026-03-31T15:30:00Z")
    narratives_top = {
        "headlines": ["Manchester City vs Arsenal: Monumental Premier League title decider"],
        "fan_comments": ["Incredible excitement, game of the season, pure fireworks!"],
        "media_articles_count": 135
    }

    num_top = num_ext.extract(fix_top)
    nlp_top = nlp_ext.extract(fix_top, narratives_top)

    ml_scorer = HybridMLScorer(random_state=42)
    assert ml_scorer.is_trained is True

    score, attributions = ml_scorer.predict_score(num_top, nlp_top)
    assert 0.0 <= score <= 100.0
    assert score >= 70.0, "Un choque por el título City vs Arsenal debe tener un Excitement Score alto"

    # Verificar cálculo de atribuciones
    assert "xg_offensive_potential" in attributions
    assert "competitive_stakes_parity" in attributions
    assert "fan_hype_and_drama" in attributions
    assert "media_coverage_and_stars" in attributions
    total_attr = sum(attributions.values())
    assert abs(total_attr - 100.0) < 1.0

    # Verificar telemetría y feature importances
    telemetry = ml_scorer.get_telemetry()
    assert telemetry.trained is True
    assert len(telemetry.feature_importances) > 0
    assert telemetry.cross_validation.optimal_weights.validate_weights() is True


def test_match_scorer_with_cv_optimal_profile():
    provider = LocalDataProvider()
    scorer = MatchScorer(data_provider=provider)

    req = RecommendationRequest(gameweek=29, profile="cv_optimal", top_n=3, model_type="weighted")
    res = scorer.recommend(req)

    assert res.profile_used == "cv_optimal"
    assert res.scoring_mode == "weighted"
    assert len(res.top_matches) == 3
    assert res.weights_applied.validate_weights() is True

    # El primer partido debe tener justificaciones semánticas
    top_match = res.top_matches[0]
    assert top_match.excitement_score >= res.top_matches[1].excitement_score
    assert len(top_match.reasons) > 0
    assert top_match.scoring_mode == "weighted"
    assert len(top_match.feature_attributions) == 4


def test_match_scorer_with_ml_hybrid_mode():
    provider = LocalDataProvider()
    scorer = MatchScorer(data_provider=provider)

    req = RecommendationRequest(gameweek=29, profile="balanced", top_n=3, model_type="ml_hybrid")
    res = scorer.recommend(req)

    assert res.scoring_mode == "ml_hybrid"
    assert len(res.top_matches) == 3

    top_match = res.top_matches[0]
    assert top_match.scoring_mode == "ml_hybrid"
    assert top_match.numerical_features.tactical_style_label is not None
    assert top_match.numerical_features.progressive_passes_combined > 0.0
    assert 0.0 <= top_match.excitement_score <= 100.0


def test_api_hybrid_cross_validation_endpoint():
    client = TestClient(app)

    response = client.get("/api/v1/hybrid/cross-validation")
    assert response.status_code == 200
    data = response.json()

    assert data["model_name"] == "HybridGradientBoostingRegressor"
    assert data["trained"] is True
    assert "cross_validation" in data
    assert data["cross_validation"]["spearman_rank_correlation"] > 0.60
    assert len(data["feature_importances"]) > 0


def test_api_recommendations_with_ml_hybrid():
    client = TestClient(app)

    payload = {
        "gameweek": 29,
        "profile": "cv_optimal",
        "top_n": 3,
        "model_type": "ml_hybrid"
    }
    response = client.post("/api/v1/recommendations/top3", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["scoring_mode"] == "ml_hybrid"
    assert data["profile_used"] == "cv_optimal"
    assert len(data["top_matches"]) == 3
    assert "feature_attributions" in data["top_matches"][0]
    assert "tactical_style_label" in data["top_matches"][0]["numerical_features"]


def test_api_fixture_analysis_with_ml_hybrid():
    client = TestClient(app)

    response = client.get("/api/v1/fixtures/101/analysis?profile=cv_optimal&model_type=ml_hybrid")
    assert response.status_code == 200
    data = response.json()

    assert data["fixture"]["id"] == 101
    assert data["scoring_mode"] == "ml_hybrid"
    assert data["excitement_score"] >= 70.0
    assert "tactical_style_label" in data["numerical_features"]
