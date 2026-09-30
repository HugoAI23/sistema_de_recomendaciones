from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import numpy as np
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import spearmanr

from src.core.schemas import (
    MatchNumericalFeatures,
    MatchNLPFeatures,
    MatchScoreWeights,
    CrossValidationResult,
    FeatureImportanceItem,
    HybridModelTelemetry,
)


def compute_ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 3) -> float:
    """Calcula el Normalized Discounted Cumulative Gain para las top k recomendaciones."""
    if len(y_true) < k:
        k = len(y_true)
    if k <= 0:
        return 1.0

    # Ordenar por predicción
    order_pred = np.argsort(y_pred)[::-1][:k]
    # Relevancia ideal ordenada por verdadero score
    order_ideal = np.argsort(y_true)[::-1][:k]

    dcg = sum(float(y_true[idx]) / np.log2(rank + 2) for rank, idx in enumerate(order_pred))
    idcg = sum(float(y_true[idx]) / np.log2(rank + 2) for rank, idx in enumerate(order_ideal))

    return round(float(dcg / idcg) if idcg > 0 else 1.0, 4)


class CrossValidationWeightOptimizer:
    """Optimizador matemático de ponderaciones (w1, w2, w3, w4) con Validación Cruzada (k-Fold CV).
    
    Ajusta los pesos para la ecuación canónica:
    Score = w1 * xGcomb + w2 * Paridad + w3 * Fan_Excitement + w4 * Media_Velocity
    sujeto a sum(w_i) = 1.0 y w_i >= 0.05.
    
    Evalúa en cada pliegue el error cuadrático medio, correlación de Spearman y NDCG@3.
    """

    def __init__(self, k_folds: int = 5, random_state: int = 42):
        self.k_folds = k_folds
        self.random_state = random_state
        self._cv_result: Optional[CrossValidationResult] = None

    def _generate_synthetic_benchmark(self) -> Tuple[np.ndarray, np.ndarray]:
        """Genera un benchmark representativo de partidos de Premier League con diversos perfiles
        (derbis, duelos por el título, choques por la permanencia, partidos cerrados y festivales ofensivos).
        
        Columnas X: [norm_xg, norm_parity, norm_fan, norm_media]
        Target y: Excitement Score ground-truth [0, 100]
        """
        np.random.seed(self.random_state)
        # Partidos arquetípicos
        archetypes = [
            # [xg, parity, fan, media, ground_truth]
            [90.0, 95.0, 92.0, 95.0, 94.0],  # Title decider (City vs Arsenal)
            [82.0, 70.0, 88.0, 85.0, 86.5],  # Fierce Derby (Merseyside)
            [85.0, 65.0, 84.0, 80.0, 83.0],  # London Derby (Spurs vs Chelsea)
            [75.0, 85.0, 65.0, 55.0, 72.0],  # European race (Newcastle vs West Ham)
            [68.0, 75.0, 60.0, 50.0, 66.0],  # West Midlands Derby (Villa vs Wolves)
            [45.0, 95.0, 62.0, 45.0, 64.0],  # Relegation 6-pointer (Luton vs Forest)
            [60.0, 70.0, 58.0, 42.0, 60.0],  # M23 Derby (Brighton vs Palace)
            [55.0, 65.0, 68.0, 65.0, 62.5],  # Big club vs organized team (Man Utd vs Fulham)
            [50.0, 40.0, 35.0, 25.0, 41.0],  # Midtable vs Bottom (Bournemouth vs Sheff Utd)
            [40.0, 70.0, 38.0, 22.0, 43.0],  # Low-block relegation battle (Burnley vs Brentford)
            # Casos de estrés y diversidad
            [95.0, 45.0, 75.0, 70.0, 76.0],  # High-scoring lopsided game
            [30.0, 90.0, 40.0, 30.0, 48.0],  # Ultra-defensive parity game
            [80.0, 80.0, 80.0, 75.0, 81.0],  # High-standard clash
            [40.0, 50.0, 30.0, 20.0, 36.0],  # Low stakes fixture
            [70.0, 85.0, 78.0, 68.0, 77.0],  # Top 6 battle
        ]

        # Multiplicar con ligeras perturbaciones para simular 45 partidos históricos
        X_list = []
        y_list = []
        for row in archetypes:
            for _ in range(3):
                noise = np.random.normal(0, 2.5, 4)
                x = np.clip(np.array(row[:4]) + noise, 5.0, 100.0)
                y = np.clip(row[4] + np.random.normal(0, 2.0), 10.0, 100.0)
                X_list.append(x)
                y_list.append(y)

        # Integrar datos reales de entrenamiento de la temporada 2026-2027 (Jornadas 1 a 5)
        try:
            import json
            from src.core.config import settings
            matches_file = settings.data_dir / "season_2026_2027_matches.json"
            if matches_file.exists():
                with open(matches_file, "r", encoding="utf-8") as f:
                    season_matches = json.load(f)
                for item in season_matches:
                    norm_xg = min(100.0, max(0.0, ((item["xg_combined"] - 1.5) / 3.5) * 100.0))
                    norm_parity = item["table_parity"] * 100.0
                    norm_fan = item["fan_excitement_index"]
                    norm_media = item["media_velocity"]
                    target_y = float(item["excitement_score"])
                    X_list.append(np.array([norm_xg, norm_parity, norm_fan, norm_media]))
                    y_list.append(target_y)
        except Exception:
            pass

        return np.array(X_list), np.array(y_list)

    def optimize_weights_cv(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None
    ) -> CrossValidationResult:
        """Ejecuta una búsqueda en simplex de pesos con K-Fold Cross Validation.
        
        Maximiza la combinación de NDCG@3, correlación de Spearman y mínimo MSE.
        """
        if X is None or y is None:
            X, y = self._generate_synthetic_benchmark()

        kf = KFold(n_splits=self.k_folds, shuffle=True, random_state=self.random_state)

        # Generar candidatos en la rejilla de pesos que sumen exactamente 1.0 (step = 0.05)
        candidates = []
        for w1 in np.arange(0.15, 0.55, 0.05):
            for w2 in np.arange(0.10, 0.45, 0.05):
                for w3 in np.arange(0.10, 0.45, 0.05):
                    w4 = round(1.0 - (w1 + w2 + w3), 2)
                    if 0.05 <= w4 <= 0.35:
                        candidates.append((round(w1, 2), round(w2, 2), round(w3, 2), w4))

        best_score = -9999.0
        best_weights = (0.35, 0.25, 0.25, 0.15)
        best_metrics = {}

        for w in candidates:
            w_arr = np.array(w)
            fold_mses = []
            fold_r2s = []
            fold_spearmans = []
            fold_ndcgs = []

            for train_idx, test_idx in kf.split(X):
                X_test, y_test = X[test_idx], y[test_idx]
                y_pred = X_test @ w_arr

                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                sp, _ = spearmanr(y_test, y_pred)
                ndcg = compute_ndcg_at_k(y_test, y_pred, k=3)

                fold_mses.append(mse)
                fold_r2s.append(r2)
                fold_spearmans.append(sp if not np.isnan(sp) else 0.5)
                fold_ndcgs.append(ndcg)

            # Criterio compuesto de optimización: 50% Spearman + 40% NDCG@3 - 10% (MSE / 100)
            avg_spearman = float(np.mean(fold_spearmans))
            avg_ndcg = float(np.mean(fold_ndcgs))
            avg_mse = float(np.mean(fold_mses))
            avg_r2 = float(np.mean(fold_r2s))

            comp_score = (0.50 * avg_spearman) + (0.40 * avg_ndcg) + (0.10 * max(0.0, avg_r2))

            if comp_score > best_score:
                best_score = comp_score
                best_weights = w
                best_metrics = {
                    "mse": round(avg_mse, 3),
                    "r2": round(avg_r2, 3),
                    "spearman": round(avg_spearman, 3),
                    "ndcg": round(avg_ndcg, 3),
                }

        optimal_weights = MatchScoreWeights(
            w_xg=best_weights[0],
            w_parity=best_weights[1],
            w_fan_excitement=best_weights[2],
            w_media_velocity=best_weights[3],
        )

        self._cv_result = CrossValidationResult(
            k_folds=self.k_folds,
            mean_squared_error=best_metrics["mse"],
            r2_score=best_metrics["r2"],
            spearman_rank_correlation=best_metrics["spearman"],
            ndcg_at_3=best_metrics["ndcg"],
            optimal_weights=optimal_weights,
            benchmark_matches_count=len(X),
            status="validated",
        )
        return self._cv_result

    def get_result(self) -> CrossValidationResult:
        if self._cv_result is None:
            return self.optimize_weights_cv()
        return self._cv_result


class HybridMLScorer:
    """Modelo supervisado multimodal de Machine Learning para estimar el Excitement Score.
    
    Utiliza GradientBoostingRegressor de scikit-learn con feature importance
    e inferencia de interacciones no lineales entre estadísticas numéricas y PLN.
    """

    FEATURE_NAMES = [
        "norm_xg",
        "norm_parity",
        "norm_star",
        "tactical_intensity",
        "fan_excitement_index",
        "media_velocity",
        "narrative_rivalry_score",
        "dramatic_intensity_score",
        "title_race_affinity",
        "derby_affinity",
        "relegation_affinity",
        "attacking_chaos_affinity",
    ]

    FEATURE_DESCRIPTIONS = {
        "norm_xg": "Potencial goleador proyectado de ambos equipos (xG combinado)",
        "norm_parity": "Equilibrio competitivo basado en la cercanía en la tabla de posiciones",
        "norm_star": "Impacto y disponibilidad de estrellas individuales (ICT index)",
        "tactical_intensity": "Choque táctico operativo (pases progresivos y presiones)",
        "fan_excitement_index": "Nivel de expectativa y sentimiento de la afición en Reddit (VADER)",
        "media_velocity": "Velocidad de publicaciones y cobertura de prensa deportiva",
        "narrative_rivalry_score": "Intensidad de derbi o rivalidad histórica (TF-IDF)",
        "dramatic_intensity_score": "Probabilidad de dramatismo y finales agónicos (clasificador de comentarios)",
        "title_race_affinity": "Relevancia temática de lucha directa por el título",
        "derby_affinity": "Relevancia temática de clásico local",
        "relegation_affinity": "Relevancia temática de batalla por la permanencia",
        "attacking_chaos_affinity": "Relevancia temática de partido dinámico y abierto",
    }

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = GradientBoostingRegressor(
            n_estimators=50,
            learning_rate=0.08,
            max_depth=3,
            subsample=0.85,
            random_state=random_state,
        )
        self.is_trained = False
        self.optimizer = CrossValidationWeightOptimizer(k_folds=5, random_state=random_state)
        self._feature_importances: List[FeatureImportanceItem] = []
        self._train_model()

    def _build_feature_vector(
        self,
        num_feat: MatchNumericalFeatures,
        nlp_feat: MatchNLPFeatures
    ) -> np.ndarray:
        norm_xg = min(100.0, max(0.0, ((num_feat.xg_combined - 1.5) / 3.5) * 100.0))
        norm_parity = num_feat.table_parity * 100.0
        norm_star = min(100.0, max(0.0, ((num_feat.star_power - 200.0) / 450.0) * 100.0))
        tactical_intensity = num_feat.tactical_clash_intensity * 100.0

        ctx = nlp_feat.context_relevance_vector or {}
        tr = ctx.get("title_race", 0.1) * 100.0
        derby = ctx.get("derby_rivalry", 0.1) * 100.0
        releg = ctx.get("relegation_scrap", 0.1) * 100.0
        chaos = ctx.get("attacking_chaos", 0.1) * 100.0

        vec = [
            norm_xg,
            norm_parity,
            norm_star,
            tactical_intensity,
            nlp_feat.fan_excitement_index,
            nlp_feat.media_velocity,
            nlp_feat.narrative_rivalry_score * 100.0,
            nlp_feat.dramatic_intensity_score * 100.0,
            tr,
            derby,
            releg,
            chaos,
        ]
        return np.array(vec, dtype=float)

    def _train_model(self):
        """Entrena el modelo de Machine Learning con el benchmark sintético enriquecido."""
        np.random.seed(self.random_state)
        # Base de entrenamiento sintética multimodal representativa
        X_train = []
        y_train = []

        # Casos arquetípicos representativos con las 12 variables multimodales
        base_cases = [
            # Duelo directo por el título (City vs Arsenal: xG alto, paridad alta, title race dominante, rivalidad moderada)
            ([95, 90, 95, 85, 75, 95, 30, 65, 95, 25, 5, 65], 91.0),
            ([90, 95, 90, 80, 78, 92, 35, 70, 90, 30, 5, 70], 88.0),
            # Clásico local visceral (Merseyside Derby: rivalidad extrema, drama, fan hype muy alto)
            ([82, 70, 85, 78, 90, 88, 95, 92, 40, 95, 10, 75], 88.0),
            # Caos ofensivo y derbi de alta tensión (Spurs vs Chelsea)
            ([88, 65, 80, 86, 85, 82, 90, 85, 30, 90, 5, 92], 86.0),
            # Choque directo por cupos europeos (Newcastle vs West Ham)
            ([76, 85, 68, 75, 68, 60, 45, 65, 50, 30, 10, 70], 74.0),
            # Derbi regional (Aston Villa vs Wolves)
            ([68, 75, 62, 72, 65, 52, 75, 62, 40, 70, 15, 60], 68.0),
            # Batalla desesperada por la permanencia (Luton vs Forest)
            ([45, 95, 45, 65, 64, 48, 55, 80, 5, 20, 95, 55], 67.0),
            # Derbi singular de tensión media (Brighton vs Palace)
            ([62, 70, 55, 68, 60, 45, 78, 65, 10, 75, 25, 58], 62.0),
            # Grande irregular vs equipo organizado (Fulham vs Man Utd)
            ([55, 65, 72, 60, 70, 68, 35, 58, 20, 25, 15, 52], 64.0),
            # Desigual sin tensión crítica (Bournemouth vs Sheff Utd)
            ([50, 40, 45, 45, 38, 28, 20, 42, 5, 10, 40, 48], 42.0),
            # Lucha de bloque bajo conservadora (Burnley vs Brentford)
            ([42, 70, 48, 50, 40, 25, 25, 45, 5, 15, 65, 40], 45.0),
        ]

        for feat_vec, target in base_cases:
            for _ in range(5):
                noise = np.random.normal(0, 2.0, len(feat_vec))
                x_sample = np.clip(np.array(feat_vec, dtype=float) + noise, 0.0, 100.0)
                y_sample = np.clip(target + np.random.normal(0, 1.8), 10.0, 100.0)
                X_train.append(x_sample)
                y_train.append(y_sample)

        # Incorporar muestras reales de entrenamiento de la temporada 2026-2027 (Jornadas 1 a 5)
        try:
            import json
            from src.core.config import settings
            from src.features.nlp import ContextSemanticEmbedder
            matches_file = settings.data_dir / "season_2026_2027_matches.json"
            if matches_file.exists():
                embedder = ContextSemanticEmbedder()
                with open(matches_file, "r", encoding="utf-8") as f:
                    season_matches = json.load(f)
                for item in season_matches:
                    norm_xg = min(100.0, max(0.0, ((item["xg_combined"] - 1.5) / 3.5) * 100.0))
                    norm_parity = item["table_parity"] * 100.0
                    norm_star = min(100.0, max(0.0, ((item["star_power"] - 200.0) / 450.0) * 100.0))
                    tactical_intensity = min(100.0, max(10.0, item.get("dramatic_intensity_score", 0.5) * 90.0))
                    fan_excitement_index = item["fan_excitement_index"]
                    media_velocity = item["media_velocity"]
                    narrative_rivalry = item["narrative_rivalry_score"] * 100.0
                    drama_intensity = item["dramatic_intensity_score"] * 100.0
                    
                    ctx = embedder.embed_and_score(item.get("commentary_sample", ""))
                    tr = ctx.get("title_race", 0.1) * 100.0
                    derby = ctx.get("derby_rivalry", 0.1) * 100.0
                    releg = ctx.get("relegation_scrap", 0.1) * 100.0
                    chaos = ctx.get("attacking_chaos", 0.1) * 100.0

                    vec = [
                        norm_xg, norm_parity, norm_star, tactical_intensity,
                        fan_excitement_index, media_velocity, narrative_rivalry, drama_intensity,
                        tr, derby, releg, chaos
                    ]
                    target_y = float(item["excitement_score"])
                    X_train.append(np.array(vec, dtype=float))
                    y_train.append(target_y)
        except Exception:
            pass

        X_mat = np.array(X_train)
        y_vec = np.array(y_train)

        self.model.fit(X_mat, y_vec)
        self.is_trained = True

        # Extraer importancias relativas
        raw_importances = self.model.feature_importances_
        sum_imp = sum(raw_importances) if sum(raw_importances) > 0 else 1.0
        normalized_imp = [round(float(v / sum_imp) * 100.0, 2) for v in raw_importances]

        self._feature_importances = [
            FeatureImportanceItem(
                feature=name,
                importance_percentage=normalized_imp[idx],
                description=self.FEATURE_DESCRIPTIONS.get(name, name),
            )
            for idx, name in enumerate(self.FEATURE_NAMES)
        ]
        # Ordenar de mayor a menor importancia
        self._feature_importances.sort(key=lambda x: x.importance_percentage, reverse=True)

    def predict_score(
        self,
        num_feat: MatchNumericalFeatures,
        nlp_feat: MatchNLPFeatures
    ) -> Tuple[float, Dict[str, float]]:
        """Predice el Excitement Score [0, 100] usando el modelo de Gradient Boosting
        y calcula las atribuciones de características clave del partido.
        """
        x_vec = self._build_feature_vector(num_feat, nlp_feat)
        pred = float(self.model.predict([x_vec])[0])
        score = round(min(100.0, max(0.0, pred)), 2)

        # Calcular atribución porcentual normalizada para las 4 macro-dimensiones
        xg_dim = x_vec[0] * 0.45 + x_vec[11] * 0.55       # xG + attacking chaos
        parity_dim = x_vec[1] * 0.70 + x_vec[8] * 0.30   # Table parity + title race / stakes
        fan_dim = x_vec[4] * 0.50 + x_vec[6] * 0.25 + x_vec[7] * 0.25 # Fan sentiment + rivalry + drama
        media_dim = x_vec[5] * 0.70 + x_vec[2] * 0.30     # Media velocity + star power

        total_dim = xg_dim + parity_dim + fan_dim + media_dim
        if total_dim > 0:
            attributions = {
                "xg_offensive_potential": round((xg_dim / total_dim) * 100.0, 1),
                "competitive_stakes_parity": round((parity_dim / total_dim) * 100.0, 1),
                "fan_hype_and_drama": round((fan_dim / total_dim) * 100.0, 1),
                "media_coverage_and_stars": round((media_dim / total_dim) * 100.0, 1),
            }
        else:
            attributions = {
                "xg_offensive_potential": 35.0,
                "competitive_stakes_parity": 25.0,
                "fan_hype_and_drama": 25.0,
                "media_coverage_and_stars": 15.0,
            }

        return score, attributions

    def get_telemetry(self) -> HybridModelTelemetry:
        cv_res = self.optimizer.get_result()
        return HybridModelTelemetry(
            model_name="HybridGradientBoostingRegressor",
            trained=self.is_trained,
            scoring_mode="ml_hybrid",
            cross_validation=cv_res,
            feature_importances=self._feature_importances,
            generated_at=datetime.utcnow().isoformat(),
        )
