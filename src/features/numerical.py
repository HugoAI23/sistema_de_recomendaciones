import math
from typing import Tuple
from src.core.schemas import Fixture, Team, MatchNumericalFeatures


class NumericalFeatureExtractor:
    """Extractor de métricas cuantitativas y tácticas para un partido de Premier League.
    
    Implementa:
    1. Expected Goals Combined (xGcomb)
    2. Índice de Paridad en la Tabla
    3. Star Player Availability (Star Power ICT)
    4. Estilo Táctico Operativo: Similitud(Pases_Progresivos, Presiones)
    5. Normalización integral de score numérico [0, 100]
    """

    def _estimate_tactical_profile(self, team: Team) -> Tuple[float, float]:
        """Estima las métricas operativas de estilo táctico:
        - Pases Progresivos por partido (PP)
        - Presiones Defensivas por partido (DP)
        basado en la pegada ofensiva (xG), solvencia defensiva y posición en tabla.
        """
        # Equipos dominantes de posesión generan más pases progresivos (ej. 45 - 65)
        # Equipos reactivos o en bloque bajo generan menos (ej. 20 - 35)
        pp = 25.0 + (team.xg_for_last5 * 11.5) + max(0.0, (21 - team.position) * 0.7)
        # Equipos que defienden en campo propio o repliegan acumulan mayores presiones defensivas
        dp = 115.0 + (team.xga_for_last5 * 24.0) + ((21 - team.position) * 0.4)
        return round(pp, 1), round(dp, 1)

    def _classify_tactical_clash(
        self,
        home_pp: float,
        home_dp: float,
        away_pp: float,
        away_dp: float,
        xg_combined: float,
    ) -> Tuple[str, float]:
        """Identifica el choque táctico operativo entre dos clubes:
        - Guerra Ofensiva Abierta (Ataque vs Ataque)
        - Asedio Táctico vs Bloque Bajo (Posesión vs Contraataque)
        - Duelo Físico de Alta Presión
        - Equilibrio Táctico Conservador
        
        Calcula la similitud/intensidad del choque en el rango [0.10 - 1.00].
        """
        is_home_attacking = home_pp >= 42.0
        is_away_attacking = away_pp >= 42.0
        is_home_high_press = home_dp >= 145.0
        is_away_high_press = away_dp >= 145.0

        if is_home_attacking and is_away_attacking:
            label = "Guerra Ofensiva Abierta (Ataque vs Ataque)"
            # Alta intensidad con enorme probabilidad de goles y llegadas
            base_intensity = 0.85
        elif (is_home_attacking and not is_away_attacking) or (not is_home_attacking and is_away_attacking):
            label = "Asedio Táctico vs Contraataque (Posesión vs Transición)"
            # Choque de estilos contrastantes, alta tensión táctica
            base_intensity = 0.72
        elif is_home_high_press and is_away_high_press:
            label = "Duelo Físico de Alta Presión y Disputa"
            base_intensity = 0.70
        else:
            label = "Equilibrio Táctico Conservador"
            base_intensity = 0.45

        # Similitud vectorial de cosenos entre perfiles tácticos (Pases Progresivos, Presiones)
        dot_product = (home_pp * away_pp) + (home_dp * away_dp)
        norm_home = math.sqrt(home_pp**2 + home_dp**2)
        norm_away = math.sqrt(away_pp**2 + away_dp**2)
        cos_sim = dot_product / (norm_home * norm_away) if (norm_home * norm_away) > 0 else 0.5

        # Ajuste fino por potencial ofensivo conjunto
        xg_factor = min(0.15, max(0.0, (xg_combined - 2.5) * 0.05))
        tactical_intensity = min(1.0, max(0.1, (base_intensity * 0.7) + (cos_sim * 0.2) + xg_factor))

        return label, round(tactical_intensity, 2)

    def extract(self, fixture: Fixture) -> MatchNumericalFeatures:
        home = fixture.home_team
        away = fixture.away_team

        # 1. Combined Expected Goals (xGcomb)
        xg_combined = round(home.xg_for_last5 + away.xg_for_last5, 2)

        # 2. Índice de Paridad en la Tabla: 1 - (|PosLocal - PosVisitante| / 20)
        pos_diff = abs(home.position - away.position)
        table_parity = round(1.0 - (pos_diff / 20.0), 3)

        # 3. Star Power (Suma de ICT de ambos planteles)
        star_power = round(home.key_players_ict + away.key_players_ict, 1)

        # 4. Estilo Táctico Operativo (Pases Progresivos y Presiones)
        home_pp, home_dp = self._estimate_tactical_profile(home)
        away_pp, away_dp = self._estimate_tactical_profile(away)
        prog_passes_comb = round(home_pp + away_pp, 1)
        def_press_comb = round(home_dp + away_dp, 1)

        tactical_label, tactical_intensity = self._classify_tactical_clash(
            home_pp=home_pp,
            home_dp=home_dp,
            away_pp=away_pp,
            away_dp=away_dp,
            xg_combined=xg_combined,
        )

        # 5. Normalizaciones individuales [0, 100]
        norm_xg = min(100.0, max(0.0, ((xg_combined - 1.5) / 3.5) * 100.0))
        norm_parity = table_parity * 100.0
        norm_star = min(100.0, max(0.0, ((star_power - 200.0) / 450.0) * 100.0))
        norm_tactical = tactical_intensity * 100.0

        # Score numérico compuesto multidimensional:
        # 40% xG + 30% Paridad + 15% Star Power + 15% Intensidad Táctica
        norm_numerical = round(
            (0.40 * norm_xg) +
            (0.30 * norm_parity) +
            (0.15 * norm_star) +
            (0.15 * norm_tactical),
            2
        )
        norm_numerical = min(100.0, max(0.0, norm_numerical))

        return MatchNumericalFeatures(
            fixture_id=fixture.id,
            xg_combined=xg_combined,
            table_parity=table_parity,
            star_power=star_power,
            tactical_clash_intensity=tactical_intensity,
            tactical_style_label=tactical_label,
            progressive_passes_combined=prog_passes_comb,
            defensive_pressures_combined=def_press_comb,
            normalized_numerical_score=norm_numerical,
        )
