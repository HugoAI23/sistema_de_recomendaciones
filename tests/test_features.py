from src.core.schemas import Team, Fixture
from src.features.numerical import NumericalFeatureExtractor
from src.features.nlp import NLPFeatureExtractor


def test_numerical_extractor_ranges():
    home = Team(
        id=1, name="Arsenal", short_name="ARS", position=1, points=64, played=28,
        xg_for_last5=2.45, xga_for_last5=0.65, form="WWWWW", key_players_ict=310.5
    )
    away = Team(
        id=3, name="Manchester City", short_name="MCI", position=3, points=63, played=28,
        xg_for_last5=2.30, xga_for_last5=0.85, form="WDWWW", key_players_ict=340.0
    )
    fixture = Fixture(
        id=101, gameweek=29, home_team=home, away_team=away,
        kickoff_time="2026-03-31T15:30:00Z", is_derby=False
    )

    extractor = NumericalFeatureExtractor()
    feat = extractor.extract(fixture)

    assert feat.xg_combined == 4.75
    assert feat.table_parity == 0.9  # 1 - |1-3|/20 = 1 - 0.1 = 0.9
    assert 0.0 <= feat.normalized_numerical_score <= 100.0


def test_nlp_extractor_sentiment_and_rivalry():
    home = Team(
        id=2, name="Liverpool", short_name="LIV", position=2, points=64, played=28,
        xg_for_last5=2.6, xga_for_last5=1.1, form="DWWWW", key_players_ict=325.0
    )
    away = Team(
        id=16, name="Everton", short_name="EVE", position=16, points=25, played=28,
        xg_for_last5=1.2, xga_for_last5=1.3, form="LDDLD", key_players_ict=145.0
    )
    fixture = Fixture(
        id=102, gameweek=29, home_team=home, away_team=away,
        kickoff_time="2026-03-30T11:30:00Z", is_derby=True, derby_name="Merseyside Derby"
    )

    narrative_data = {
        "headlines": ["Merseyside Derby: Fierce local derby rivalry at Anfield"],
        "fan_comments": ["Brutal battle, great intense excitement and electric atmosphere!"],
        "media_articles_count": 95,
    }

    extractor = NLPFeatureExtractor()
    feat = extractor.extract(fixture, narrative_data)

    assert 0.0 <= feat.fan_excitement_index <= 100.0
    assert 0.0 <= feat.media_velocity <= 100.0
    assert feat.narrative_rivalry_score > 0.3
    assert 0.0 <= feat.normalized_nlp_score <= 100.0
