import argparse
from src.core.config import settings
from src.core.schemas import RecommendationRequest
from src.data_ingestion.local_provider import LocalDataProvider
from src.data_ingestion.fpl_client import FPLDataProvider
from src.engine.scorer import MatchScorer


def run_cli():
    parser = argparse.ArgumentParser(description="Premier League Match Recommender CLI (Fase 4: API REST & Dashboard)")
    parser.add_argument("--gameweek", "-g", type=int, default=8, help="Jornada a consultar (ej: 8)")
    parser.add_argument("--date", "-d", type=str, default=None, help="Filtrar por fecha específica (YYYY-MM-DD, ej: 2026-03-31)")
    parser.add_argument(
        "--profile", "-p",
        choices=["balanced", "cv_optimal", "goal_fest", "tension", "fan_hype"],
        default="cv_optimal",
        help="Perfil de recomendación (default: cv_optimal)"
    )
    parser.add_argument(
        "--model", "-m",
        choices=["weighted", "ml_hybrid"],
        default="weighted",
        help="Motor de scoring: 'weighted' (fórmula canónica) o 'ml_hybrid' (Gradient Boosting ML)"
    )
    parser.add_argument("--top", "-n", type=int, default=3, help="Cantidad de partidos a recomendar (default: 3)")
    parser.add_argument("--offline", action="store_true", help="Forzar solo datos locales offline")
    parser.add_argument("--cv-report", action="store_true", help="Mostrar reporte de validación cruzada y pesos óptimos")

    args = parser.parse_args()

    local_prov = LocalDataProvider()
    provider = local_prov if args.offline else FPLDataProvider(fallback_provider=local_prov)
    scorer = MatchScorer(data_provider=provider)

    if args.cv_report:
        telemetry = scorer.ml_scorer.get_telemetry()
        cv = telemetry.cross_validation
        w = cv.optimal_weights
        print("\n" + "=" * 75)
        print(" 🧪 REPORTE DE VALIDACIÓN CRUZADA K-FOLD Y MOTOR DE MACHINE LEARNING")
        print("=" * 75)
        print(f" • Modelo Base: {telemetry.model_name} (Entrenado: {telemetry.trained})")
        print(f" • Partidos Benchmark Evaluados: {cv.benchmark_matches_count} en {cv.k_folds} pliegues")
        print(f" • Métricas de Ranking y Calibración:")
        print(f"    - Spearman Rank Correlation: {cv.spearman_rank_correlation:.3f}")
        print(f"    - NDCG@3 (Ranking Calidad Top 3): {cv.ndcg_at_3:.3f}")
        print(f"    - Mean Squared Error (MSE): {cv.mean_squared_error:.3f}")
        print(f"    - Coeficiente R2: {cv.r2_score:.3f}")
        print(f"\n ⚖️  Pesos Óptimos Calibrados (Preset 'cv_optimal'):")
        print(f"    w_xg = {w.w_xg:.2f} | w_parity = {w.w_parity:.2f} | w_fan = {w.w_fan_excitement:.2f} | w_media = {w.w_media_velocity:.2f}")
        print(f"\n 📊 Importancia de Variables en el Modelo ML (Gradient Boosting):")
        for item in telemetry.feature_importances[:6]:
            print(f"    - {item.feature:25s}: {item.importance_percentage:5.1f}%  ({item.description})")
        print("=" * 75 + "\n")
        return

    req = RecommendationRequest(
        gameweek=args.gameweek,
        date=args.date,
        profile=args.profile,
        top_n=args.top,
        model_type=args.model,
    )
    res = scorer.recommend(req)

    print("\n" + "=" * 75)
    date_str = f" | Fecha: {res.date_filter}" if res.date_filter else ""
    print(f" ⚽ PREMIER LEAGUE MATCH RECOMMENDER — TOP {args.top} PARTIDOS (Jornada {res.gameweek}{date_str})")
    print(f" ⚙️  Perfil: '{res.profile_used.upper()}' | Motor: '{res.scoring_mode.upper()}' (Fase 4)")
    print("=" * 75)

    for match in res.top_matches:
        home = match.fixture.home_team
        away = match.fixture.away_team
        num = match.numerical_features
        nlp = match.nlp_features
        print(f"\n🏆 #{match.rank} | {home.name} (#{home.position}) vs {away.name} (#{away.position})")
        print(f"   ⭐ Excitement Score: {match.excitement_score}/100")
        print(f"   🎯 Choque Táctico: {num.tactical_style_label} (Intensidad: {int(num.tactical_clash_intensity*100)}%)")
        print(f"   📊 Métricas Clave:")
        print(f"      - xG Combinado: {num.xg_combined} | Paridad: {int(num.table_parity*100)}% | Star Power: {num.star_power}")
        print(f"      - Sentimiento Afición: {nlp.fan_excitement_index}/100 | Cobertura Prensa: {nlp.media_velocity}/100")
        if match.feature_attributions:
            att = match.feature_attributions
            print(f"   📈 Atribución de Factores: xG {att.get('xg_offensive_potential', 0)}% | Tabla {att.get('competitive_stakes_parity', 0)}% | Hype {att.get('fan_hype_and_drama', 0)}% | Prensa {att.get('media_coverage_and_stars', 0)}%")
        print(f"   💡 Justificación Semántica:")
        for reason in match.reasons:
            print(f"      • [{reason.category}] {reason.title}")
            print(f"        {reason.description}")

    print("\n" + "=" * 75)
    print(f" Evaluados {res.total_evaluated_matches} encuentros en total. Motor Híbrido Multimodal (Fase 4: API REST & Dashboard).\n")


if __name__ == "__main__":
    run_cli()
