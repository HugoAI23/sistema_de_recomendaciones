from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Depends
from src.core.config import settings
from src.core.schemas import (
    Fixture,
    Team,
    RecommendationRequest,
    RecommendationResponse,
    ScoredMatch,
    MatchScoreWeights,
    HybridModelTelemetry,
)
from src.data_ingestion.local_provider import LocalDataProvider
from src.data_ingestion.fpl_client import FPLDataProvider
from src.engine.scorer import MatchScorer

from fastapi.responses import HTMLResponse
from src.api.dashboard import get_dashboard_html

router = APIRouter()

# Inyección de dependencias para el proveedor y scorer
def get_scorer() -> MatchScorer:
    # Usamos FPLDataProvider con fallback automático a LocalDataProvider
    local_prov = LocalDataProvider()
    fpl_prov = FPLDataProvider(fallback_provider=local_prov)
    return MatchScorer(data_provider=fpl_prov)


@router.get("/health", tags=["Sistema"])
def health_check():
    """Verifica la salud del microservicio y sus dependencias."""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version,
        "zero_cost_mode": True,
        "active_data_source": "FPL Public API + Local Fallback",
        "phase_completed": "Fase 4: API REST & Panel Interactivo",
    }


@router.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
def get_dashboard():
    """Sirve el panel web interactivo para explorar recomendaciones y partidos en vivo."""
    return HTMLResponse(content=get_dashboard_html(), status_code=200)


@router.get("/profiles", response_model=Dict[str, MatchScoreWeights], tags=["Recomendaciones"])
def list_profiles():
    """Retorna los perfiles de ponderación predefinidos (incluyendo 'cv_optimal')."""
    return settings.weight_profiles


@router.get("/teams", response_model=List[Team], tags=["Premier League"])
def get_teams(scorer: MatchScorer = Depends(get_scorer)):
    """Retorna la tabla y estadísticas tácticas de los 20 clubes."""
    return scorer.provider.get_teams()


@router.get("/fixtures", response_model=List[Fixture], tags=["Premier League"])
def get_fixtures(
    gameweek: Optional[int] = Query(None, description="Filtrar por número de jornada (1-38)"),
    date: Optional[str] = Query(None, description="Filtrar por fecha específica (YYYY-MM-DD)"),
    scorer: MatchScorer = Depends(get_scorer)
):
    """Lista los partidos disponibles de la jornada y/o fecha."""
    return scorer.provider.get_fixtures(gameweek=gameweek, date=date)


@router.get("/recommendations/top3", response_model=RecommendationResponse, tags=["Recomendaciones"])
def get_top3_recommendations_get(
    gameweek: Optional[int] = Query(None, description="Número de jornada a consultar (ej: 29)"),
    date: Optional[str] = Query(None, description="Filtrar por fecha de la jornada (YYYY-MM-DD)"),
    profile: str = Query("cv_optimal", description="Perfil de ponderación: 'cv_optimal', 'balanced', 'goal_fest', 'tension', 'fan_hype'"),
    model_type: str = Query("weighted", description="Modo del motor: 'weighted' o 'ml_hybrid'"),
    top_n: int = Query(3, ge=1, le=10, description="Cantidad de partidos a recomendar"),
    scorer: MatchScorer = Depends(get_scorer)
):
    """Calcula y devuelve los 3 mejores partidos recomendados mediante método GET con parámetros de consulta."""
    req = RecommendationRequest(
        gameweek=gameweek,
        date=date,
        profile=profile,
        top_n=top_n,
        model_type=model_type,
    )
    return scorer.recommend(req)


@router.post("/recommendations/top3", response_model=RecommendationResponse, tags=["Recomendaciones"])
def get_top3_recommendations(
    request: Optional[RecommendationRequest] = None,
    scorer: MatchScorer = Depends(get_scorer)
):
    """Calcula y devuelve los 3 mejores partidos recomendados con sus justificaciones semánticas.
    Soporta scoring ponderado canónico o Machine Learning híbrido ('ml_hybrid'), filtros de jornada y fecha.
    """
    req = request or RecommendationRequest(top_n=3)
    return scorer.recommend(req)


@router.get("/fixtures/{fixture_id}/analysis", response_model=ScoredMatch, tags=["Recomendaciones"])
def get_fixture_analysis(
    fixture_id: int,
    profile: str = Query("balanced", description="Perfil de ponderación: 'balanced', 'cv_optimal', etc."),
    model_type: str = Query("weighted", description="Modo: 'weighted' o 'ml_hybrid'"),
    scorer: MatchScorer = Depends(get_scorer)
):
    """Entrega un análisis exhaustivo cuantitativo y PLN de un partido particular."""
    fixtures = scorer.provider.get_fixtures()
    matched = next((f for f in fixtures if f.id == fixture_id), None)
    if not matched:
        raise HTTPException(status_code=404, detail=f"Partido con id {fixture_id} no encontrado")

    if profile == "cv_optimal":
        weights = scorer.ml_scorer.optimizer.get_result().optimal_weights
    else:
        weights = settings.weight_profiles.get(profile, settings.weight_profiles["balanced"])

    return scorer.score_match(matched, weights, scoring_mode=model_type)


@router.get("/hybrid/cross-validation", response_model=HybridModelTelemetry, tags=["Motor Híbrido ML"])
def get_hybrid_cross_validation_telemetry(scorer: MatchScorer = Depends(get_scorer)):
    """Retorna las métricas de validación cruzada k-Fold (MSE, Spearman, NDCG@3),
    los pesos óptimos calculados y la importancia de variables del modelo ML.
    """
    return scorer.ml_scorer.get_telemetry()
