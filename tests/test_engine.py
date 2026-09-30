from src.data_ingestion.local_provider import LocalDataProvider
from src.engine.scorer import MatchScorer
from src.core.schemas import RecommendationRequest


def test_match_scorer_recommendation_order():
    provider = LocalDataProvider()
    scorer = MatchScorer(data_provider=provider)

    req = RecommendationRequest(gameweek=29, profile="balanced", top_n=3)
    response = scorer.recommend(req)

    assert len(response.top_matches) == 3
    assert response.gameweek == 29

    scores = [m.excitement_score for m in response.top_matches]
    assert scores == sorted(scores, reverse=True), "Los partidos deben estar ordenados descendentemente"

    # Verificar que el partido líder tiene justificaciones
    top_match = response.top_matches[0]
    assert len(top_match.reasons) > 0
    assert any(r.category == "DERBI / RIVALIDAD" or r.category == "DUELO EN LA CIMA" for r in top_match.reasons)


def test_scorer_with_goal_fest_profile():
    provider = LocalDataProvider()
    scorer = MatchScorer(data_provider=provider)

    req_balanced = RecommendationRequest(gameweek=29, profile="balanced", top_n=5)
    req_goals = RecommendationRequest(gameweek=29, profile="goal_fest", top_n=5)

    res_balanced = scorer.recommend(req_balanced)
    res_goals = scorer.recommend(req_goals)

    assert res_balanced.profile_used == "balanced"
    assert res_goals.profile_used == "goal_fest"
