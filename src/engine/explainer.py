from typing import List, Optional, Dict
from src.core.schemas import Fixture, MatchNumericalFeatures, MatchNLPFeatures, RecommendationReason


class SemanticExplainer:
    """Generador semántico de justificaciones explicativas para los partidos recomendados."""

    def explain(
        self,
        fixture: Fixture,
        num_feat: MatchNumericalFeatures,
        nlp_feat: MatchNLPFeatures,
        attributions: Optional[Dict[str, float]] = None,
    ) -> List[RecommendationReason]:
        reasons: List[RecommendationReason] = []
        home = fixture.home_team
        away = fixture.away_team

        # 1. Justificación por Derbi o Rivalidad Histórica
        if fixture.is_derby or nlp_feat.narrative_rivalry_score >= 0.5:
            title = fixture.derby_name or f"Rivalidad Directa: {home.name} vs {away.name}"
            reasons.append(RecommendationReason(
                category="DERBI / RIVALIDAD",
                title=title,
                description=f"Partido de máxima tensión y orgullo local con una calificación de rivalidad narrativa de {nlp_feat.narrative_rivalry_score:.2f}/1.00."
            ))

        # 2. Justificación por Estilo Táctico Operativo (Fase 3)
        if num_feat.tactical_clash_intensity >= 0.70:
            reasons.append(RecommendationReason(
                category="CHOQUE TÁCTICO",
                title=f"{num_feat.tactical_style_label} ({int(num_feat.tactical_clash_intensity * 100)}% de intensidad)",
                description=(
                    f"Duelo de alta fricción táctica: se proyectan {num_feat.progressive_passes_combined:.0f} pases "
                    f"progresivos y {num_feat.defensive_pressures_combined:.0f} presiones defensivas acumuladas entre ambos conjuntos."
                )
            ))

        # 3. Justificación por Dramatismo Narrativo y Volatilidad (Fase 2)
        if nlp_feat.dramatic_intensity_score >= 0.70:
            reasons.append(RecommendationReason(
                category="DRAMATISMO HISTÓRICO",
                title=f"Alta propensión a desenlace épico ({int(nlp_feat.dramatic_intensity_score * 100)}% de dramatismo)",
                description="El historial narrativo y análisis táctico anticipan un duelo volátil con alta probabilidad de desenlaces dramáticos, goles tardíos o alta fricción."
            ))

        # 4. Justificación por Potencial Ofensivo y Espectáculo (xG)
        if num_feat.xg_combined >= 3.8:
            reasons.append(RecommendationReason(
                category="FESTIVAL OFENSIVO",
                title=f"Alto potencial goleador ({num_feat.xg_combined:.2f} xG proyectado)",
                description=f"Ambos clubes llegan con enorme pegada: {home.name} ({home.xg_for_last5:.2f} xG/partido) y {away.name} ({away.xg_for_last5:.2f} xG/partido)."
            ))
        elif num_feat.xg_combined >= 3.0:
            reasons.append(RecommendationReason(
                category="DINAMISMO OFENSIVO",
                title=f"Volumen de ataque consistente ({num_feat.xg_combined:.2f} xG proyectado)",
                description="Se proyecta un encuentro abierto con múltiples ocasiones en ambas áreas."
            ))

        # 5. Justificación por Posición en la Tabla y Lo Que Está en Juego
        pos_diff = abs(home.position - away.position)
        if home.position <= 4 and away.position <= 4:
            reasons.append(RecommendationReason(
                category="DUELO EN LA CIMA",
                title=f"Choque directo por el título (#{home.position} vs #{away.position})",
                description=f"Separados por solo {abs(home.points - away.points)} puntos, el resultado impactará directamente la punta de la Premier League."
            ))
        elif home.position >= 16 and away.position >= 16:
            reasons.append(RecommendationReason(
                category="BATALLA POR LA PERMANENCIA",
                title=f"Duelo dramático de 6 puntos por no descender",
                description=f"{home.name} (#{home.position}) y {away.name} (#{away.position}) disputan un choque de alta angustia competitiva."
            ))
        elif pos_diff <= 2:
            reasons.append(RecommendationReason(
                category="PARIDAD MÁXIMA",
                title=f"Duelo directo en la clasificación (Puestos #{home.position} y #{away.position})",
                description=f"Índice de paridad del {int(num_feat.table_parity * 100)}%, pronosticando un choque extremadamente equilibrado."
            ))

        # 6. Justificación por Hype de la Afición y Foco Mediático
        if nlp_feat.fan_excitement_index >= 60.0 or nlp_feat.media_velocity >= 75.0:
            trend_str = ", ".join(f"#{kw}" for kw in nlp_feat.trending_keywords[:3]) if nlp_feat.trending_keywords else "Premier League"
            reasons.append(RecommendationReason(
                category="TENDENCIA Y VIRALIDAD",
                title=f"Gran expectativa en afición y prensa (Velocidad Mediática: {nlp_feat.media_velocity:.0f}%)",
                description=f"Fuerte conversación social con foco en: {trend_str}."
            ))

        # 7. Justificación por Disponibilidad de Estrellas (Star Power ICT)
        if num_feat.star_power >= 480.0:
            reasons.append(RecommendationReason(
                category="FIGURAS ESTRELLA",
                title=f"Elenco de alta jerarquía ({num_feat.star_power:.1f} Star Power ICT)",
                description=f"Presencia asegurada de futbolistas de élite y desequilibrio individual en el campo."
            ))

        # Fallback si no saltó ninguna regla específica
        if not reasons:
            reasons.append(RecommendationReason(
                category="INTERÉS GENERAL",
                title="Choque competitivo de Premier League",
                description="Encuentro con buen balance de equilibrio táctico y expectativa futbolística."
            ))

        return reasons
