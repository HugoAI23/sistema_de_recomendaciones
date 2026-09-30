from typing import List, Optional
from datetime import datetime
from src.core.config import settings
from src.core.schemas import (
    Fixture,
    MatchNumericalFeatures,
    MatchNLPFeatures,
    MatchScoreWeights,
    ScoredMatch,
    RecommendationResponse,
    RecommendationRequest,
)
from src.features.numerical import NumericalFeatureExtractor
from src.features.nlp import NLPFeatureExtractor
from src.engine.explainer import SemanticExplainer
from src.engine.hybrid_model import HybridMLScorer
from src.data_ingestion.base import BaseDataProvider


class MatchScorer:
    """Motor principal de scoring híbrido y ranking multimodal de partidos de Premier League."""

    def __init__(
        self,
        data_provider: BaseDataProvider,
        numerical_extractor: Optional[NumericalFeatureExtractor] = None,
        nlp_extractor: Optional[NLPFeatureExtractor] = None,
        explainer: Optional[SemanticExplainer] = None,
        ml_scorer: Optional[HybridMLScorer] = None,
    ):
        self.provider = data_provider
        self.num_ext = numerical_extractor or NumericalFeatureExtractor()
        self.nlp_ext = nlp_extractor or NLPFeatureExtractor()
        self.explainer = explainer or SemanticExplainer()
        self.ml_scorer = ml_scorer or HybridMLScorer()

    def score_match(
        self,
        fixture: Fixture,
        weights: MatchScoreWeights,
        scoring_mode: str = "weighted"
    ) -> ScoredMatch:
        narrative_data = self.provider.get_narratives(fixture.id)

        # Extracción de características multimodales
        num_feat = self.num_ext.extract(fixture)
        nlp_feat = self.nlp_ext.extract(fixture, narrative_data)

        # Normalizaciones individuales para la fórmula canónica [0, 100]
        norm_xg = min(100.0, max(0.0, ((num_feat.xg_combined - 1.5) / 3.5) * 100.0))
        norm_parity = num_feat.table_parity * 100.0
        norm_fan = nlp_feat.fan_excitement_index
        norm_media = nlp_feat.media_velocity

        if scoring_mode == "ml_hybrid":
            # Modo Machine Learning supervisado (GradientBoostingRegressor)
            final_score, attributions = self.ml_scorer.predict_score(num_feat, nlp_feat)
        else:
            # Modo Ponderado Canónico: Score = w1*xG + w2*Paridad + w3*Fan + w4*Media
            xg_contrib = weights.w_xg * norm_xg
            parity_contrib = weights.w_parity * norm_parity
            fan_contrib = weights.w_fan_excitement * norm_fan
            media_contrib = weights.w_media_velocity * norm_media

            raw_score = xg_contrib + parity_contrib + fan_contrib + media_contrib
            final_score = round(min(100.0, max(0.0, raw_score)), 2)

            total_contrib = raw_score if raw_score > 0 else 1.0
            attributions = {
                "xg_offensive_potential": round((xg_contrib / total_contrib) * 100.0, 1),
                "competitive_stakes_parity": round((parity_contrib / total_contrib) * 100.0, 1),
                "fan_hype_and_drama": round((fan_contrib / total_contrib) * 100.0, 1),
                "media_coverage_and_stars": round((media_contrib / total_contrib) * 100.0, 1),
            }

        # Generar razones explicativas contextuales
        reasons = self.explainer.explain(fixture, num_feat, nlp_feat, attributions=attributions)

        return ScoredMatch(
            fixture=fixture,
            numerical_features=num_feat,
            nlp_features=nlp_feat,
            excitement_score=final_score,
            reasons=reasons,
            scoring_mode=scoring_mode,
            feature_attributions=attributions,
        )

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        scoring_mode = request.model_type if request.model_type in ["weighted", "ml_hybrid"] else "weighted"

        # Determinar ponderaciones aplicadas
        if request.custom_weights:
            weights = request.custom_weights
            profile_name = "custom"
        elif request.profile == "cv_optimal":
            profile_name = "cv_optimal"
            weights = self.ml_scorer.optimizer.get_result().optimal_weights
        else:
            profile_name = request.profile if request.profile in settings.weight_profiles else "balanced"
            weights = settings.weight_profiles[profile_name]

        # Obtener partidos de la jornada y/o fecha
        fixtures = self.provider.get_fixtures(gameweek=request.gameweek, date=request.date)
        if not fixtures and request.date is None:
            fixtures = self.provider.get_fixtures()

        scored_matches: List[ScoredMatch] = []
        for f in fixtures:
            scored = self.score_match(f, weights, scoring_mode=scoring_mode)
            scored_matches.append(scored)

        # Ordenar de mayor a menor Excitement Score
        scored_matches.sort(key=lambda m: m.excitement_score, reverse=True)

        # Asignar rank
        for idx, m in enumerate(scored_matches, start=1):
            m.rank = idx

        top_matches = scored_matches[: request.top_n]
        gameweek_val = request.gameweek or (fixtures[0].gameweek if fixtures else 1)

        return RecommendationResponse(
            gameweek=gameweek_val,
            date_filter=request.date,
            total_evaluated_matches=len(scored_matches),
            profile_used=profile_name,
            weights_applied=weights,
            scoring_mode=scoring_mode,
            top_matches=top_matches,
            generated_at=datetime.utcnow().isoformat(),
        )
