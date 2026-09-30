import pytest
from pydantic import ValidationError
from src.core.schemas import (
    Team,
    Fixture,
    MatchNumericalFeatures,
    MatchNLPFeatures,
    MatchScoreWeights,
    RecommendationRequest,
)


def test_team_schema_validation():
    team = Team(
        id=1,
        name="Arsenal",
        short_name="ARS",
        position=1,
        points=64,
        played=28,
        xg_for_last5=2.45,
        xga_for_last5=0.65,
        form="WWWWW",
        key_players_ict=310.5,
        rivals=["Tottenham Hotspur"],
    )
    assert team.name == "Arsenal"
    assert team.position == 1

    # Validación de posición inválida fuera de rango (1-20)
    with pytest.raises(ValidationError):
        Team(
            id=99,
            name="Invalid FC",
            short_name="INV",
            position=25,
            points=10,
            played=28,
        )


def test_weights_validation():
    w = MatchScoreWeights(w_xg=0.35, w_parity=0.25, w_fan_excitement=0.25, w_media_velocity=0.15)
    assert w.validate_weights() is True

    bad_w = MatchScoreWeights(w_xg=0.8, w_parity=0.8, w_fan_excitement=0.2, w_media_velocity=0.2)
    assert bad_w.validate_weights() is False
