from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Team(BaseModel):
    id: int
    name: str
    short_name: str
    position: int = Field(ge=1, le=20, description="Posición actual en la tabla (1-20)")
    points: int = Field(ge=0, description="Puntos acumulados")
    played: int = Field(ge=0, description="Partidos jugados")
    xg_for_last5: float = Field(ge=0.0, default=1.5, description="Promedio de xG generado en los últimos 5 partidos")
    xga_for_last5: float = Field(ge=0.0, default=1.2, description="Promedio de xG concedido en los últimos 5 partidos")
    form: str = Field(default="DDDDD", description="Últimos 5 resultados (W, D, L)")
    key_players_ict: float = Field(ge=0.0, default=150.0, description="Suma acumulada del ICT Index de jugadores clave")
    rivals: List[str] = Field(default_factory=list, description="Lista de clubes con rivalidad histórica")


class Fixture(BaseModel):
    id: int
    gameweek: int = Field(ge=1, le=38, description="Número de jornada")
    home_team: Team
    away_team: Team
    kickoff_time: str
    is_derby: bool = False
    derby_name: Optional[str] = None


class MatchNumericalFeatures(BaseModel):
    fixture_id: int
    xg_combined: float = Field(description="xG Local + xG Visitante proyectado")
    table_parity: float = Field(ge=0.0, le=1.0, description="1 - |PosL - PosV| / 20")
    star_power: float = Field(ge=0.0, description="Suma de ICT de ambos planteles")
    tactical_clash_intensity: float = Field(ge=0.0, le=1.0, default=0.5, description="Intensidad de choque de estilos")
    tactical_style_label: str = Field(default="Equilibrio Táctico", description="Arquetipo de choque táctico")
    progressive_passes_combined: float = Field(default=85.0, description="Suma de pases progresivos proyectados")
    defensive_pressures_combined: float = Field(default=280.0, description="Suma de presiones defensivas proyectadas")
    normalized_numerical_score: float = Field(ge=0.0, le=100.0, description="Puntaje numérico normalizado [0-100]")


class MatchNLPFeatures(BaseModel):
    fixture_id: int
    fan_excitement_index: float = Field(ge=0.0, le=100.0, description="Índice de hype y sentimiento de la afición [0-100]")
    sentiment_compound: float = Field(ge=-1.0, le=1.0, description="Compound de VADER")
    media_velocity: float = Field(ge=0.0, le=100.0, description="Velocidad y aceleración de cobertura de noticias [0-100]")
    narrative_rivalry_score: float = Field(ge=0.0, le=1.0, description="Similitud TF-IDF con léxico de derbi/tensión")
    context_relevance_vector: Dict[str, float] = Field(
        default_factory=dict,
        description="Afinidad proyectada con ejes narrativos (title_race, derby_rivalry, relegation_scrap, attacking_chaos)"
    )
    dramatic_intensity_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Probabilidad de dramatismo narrativo y volatilidad histórica [0-1.0]"
    )
    comments_volume: int = Field(default=0, ge=0, description="Volumen total de comentarios analizados")
    comment_velocity_per_min: float = Field(default=0.0, ge=0.0, description="Densidad de comentarios por minuto")
    trending_keywords: List[str] = Field(default_factory=list, description="Palabras clave detectadas en prensa y foros")
    sample_headlines: List[str] = Field(default_factory=list, description="Titulares representativos de noticias")
    normalized_nlp_score: float = Field(ge=0.0, le=100.0, description="Puntaje de PLN normalizado [0-100]")


class MatchScoreWeights(BaseModel):
    w_xg: float = Field(default=0.35, ge=0.0, le=1.0, description="Peso para xG combinado")
    w_parity: float = Field(default=0.25, ge=0.0, le=1.0, description="Peso para paridad en tabla")
    w_fan_excitement: float = Field(default=0.25, ge=0.0, le=1.0, description="Peso para sentimiento/hype en foros")
    w_media_velocity: float = Field(default=0.15, ge=0.0, le=1.0, description="Peso para tensión y cobertura de prensa")

    def validate_weights(self) -> bool:
        total = self.w_xg + self.w_parity + self.w_fan_excitement + self.w_media_velocity
        return abs(total - 1.0) < 1e-4


class RecommendationReason(BaseModel):
    category: str = Field(description="Categoría (ej: DERBI, GOLES, TABLA, HYPE, TÁCTICA)")
    title: str
    description: str


class ScoredMatch(BaseModel):
    fixture: Fixture
    numerical_features: MatchNumericalFeatures
    nlp_features: MatchNLPFeatures
    excitement_score: float = Field(ge=0.0, le=100.0, description="Excitement Score ponderado final")
    rank: Optional[int] = None
    reasons: List[RecommendationReason] = Field(default_factory=list)
    scoring_mode: str = Field(default="weighted", description="Modo aplicado: 'weighted' o 'ml_hybrid'")
    feature_attributions: Dict[str, float] = Field(
        default_factory=dict,
        description="Aporte porcentual relativo de cada dimensión al score [0-100%]"
    )


class RecommendationRequest(BaseModel):
    gameweek: Optional[int] = None
    date: Optional[str] = Field(default=None, description="Filtrar por fecha en formato YYYY-MM-DD")
    profile: str = Field(default="balanced", description="Perfil: 'balanced', 'goal_fest', 'tension', 'fan_hype', 'cv_optimal'")
    custom_weights: Optional[MatchScoreWeights] = None
    top_n: int = Field(default=3, ge=1, le=10)
    model_type: str = Field(default="weighted", description="Modo del motor: 'weighted' o 'ml_hybrid'")


class RecommendationResponse(BaseModel):
    gameweek: int
    date_filter: Optional[str] = Field(default=None, description="Filtro de fecha aplicado si existe")
    total_evaluated_matches: int
    profile_used: str
    weights_applied: MatchScoreWeights
    scoring_mode: str = Field(default="weighted", description="Modo de evaluación: 'weighted' o 'ml_hybrid'")
    top_matches: List[ScoredMatch]
    generated_at: str


class CrossValidationResult(BaseModel):
    k_folds: int = Field(default=5, description="Número de folds utilizados")
    mean_squared_error: float = Field(description="Mean Squared Error medio (MSE)")
    r2_score: float = Field(description="Coeficiente de determinación R2")
    spearman_rank_correlation: float = Field(description="Correlación de orden de Spearman")
    ndcg_at_3: float = Field(description="NDCG para el ranking Top 3")
    optimal_weights: MatchScoreWeights = Field(description="Pesos optimizados por validación cruzada")
    benchmark_matches_count: int = Field(description="Cantidad de partidos evaluados en el benchmark")
    status: str = Field(default="validated", description="Estado de la calibración")


class FeatureImportanceItem(BaseModel):
    feature: str
    importance_percentage: float = Field(ge=0.0, le=100.0)
    description: str


class HybridModelTelemetry(BaseModel):
    model_name: str
    trained: bool
    scoring_mode: str
    cross_validation: CrossValidationResult
    feature_importances: List[FeatureImportanceItem]
    generated_at: str
