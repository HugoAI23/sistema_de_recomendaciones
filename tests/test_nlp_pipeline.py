from src.core.schemas import Team, Fixture
from src.data_ingestion.reddit_extractor import RedditNarrativeExtractor
from src.data_ingestion.news_extractor import NewsNarrativeExtractor
from src.features.commentary_classifier import CommentaryDramaClassifier
from src.features.nlp import ContextSemanticEmbedder, NLPFeatureExtractor


def _sample_fixtures():
    arsenal = Team(
        id=1, name="Arsenal", short_name="ARS", position=1, points=64, played=28,
        xg_for_last5=2.45, xga_for_last5=0.65, form="WWWWW", key_players_ict=310.5
    )
    city = Team(
        id=3, name="Manchester City", short_name="MCI", position=3, points=63, played=28,
        xg_for_last5=2.30, xga_for_last5=0.85, form="WDWWW", key_players_ict=340.0
    )
    luton = Team(
        id=18, name="Luton Town", short_name="LUT", position=18, points=21, played=28,
        xg_for_last5=1.1, xga_for_last5=2.1, form="LLDLD", key_players_ict=120.0
    )
    forest = Team(
        id=17, name="Nottingham Forest", short_name="NFO", position=17, points=22, played=28,
        xg_for_last5=1.2, xga_for_last5=1.8, form="LLLLD", key_players_ict=135.0
    )

    title_fix = Fixture(
        id=101, gameweek=29, home_team=city, away_team=arsenal,
        kickoff_time="2026-03-31T15:30:00Z", is_derby=False
    )
    derby_fix = Fixture(
        id=102, gameweek=29, home_team=arsenal, away_team=city,
        kickoff_time="2026-03-30T11:30:00Z", is_derby=True, derby_name="North London Derby"
    )
    relegation_fix = Fixture(
        id=106, gameweek=29, home_team=luton, away_team=forest,
        kickoff_time="2026-03-30T15:00:00Z", is_derby=False
    )

    return title_fix, derby_fix, relegation_fix


def test_reddit_extractor_fallback_and_properties():
    title_fix, derby_fix, _ = _sample_fixtures()
    extractor = RedditNarrativeExtractor()

    res = extractor.extract_fixture_discussion(title_fix)
    assert "fan_comments" in res
    assert res["comments_count"] >= 1000
    assert res["comment_velocity"] > 5.0
    assert res["is_live"] is False

    derby_res = extractor.extract_fixture_discussion(derby_fix)
    assert derby_res["comments_count"] > 800
    assert derby_res["total_karma"] > 1000


def test_news_extractor_fallback():
    title_fix, _, _ = _sample_fixtures()
    extractor = NewsNarrativeExtractor()

    res = extractor.extract_fixture_news(title_fix)
    assert "headlines" in res
    assert len(res["headlines"]) > 0
    assert res["media_articles_count"] >= 20
    assert res["is_live"] is False


def test_commentary_drama_classifier_discrimination():
    classifier = CommentaryDramaClassifier()

    dramatic_text = (
        "Pure madness at the Etihad! 94th minute stoppage time winner after frantic end to end chaos, "
        "furious brawl, and dramatic red card turnaround."
    )
    boring_text = (
        "Methodical and slow tempo afternoon match with routine midfield passing, low intensity "
        "and uneventful possession battle."
    )

    score_drama = classifier.predict_drama_score(dramatic_text, is_derby=True, table_diff=1)
    score_boring = classifier.predict_drama_score(boring_text, is_derby=False, table_diff=12)

    assert 0.0 <= score_drama <= 1.0
    assert 0.0 <= score_boring <= 1.0
    assert score_drama > score_boring
    assert score_drama >= 0.70


def test_context_semantic_embedder_axes():
    embedder = ContextSemanticEmbedder()

    title_text = "Huge title decider showdown clash for first place championship leaders"
    relegation_text = "Desperate relegation dogfight drop zone six pointer survival battle"
    derby_text = "Hostile local derby fierce rivalry intense tackles bad blood bragging rights"

    vec_title = embedder.embed_and_score(title_text)
    vec_relegation = embedder.embed_and_score(relegation_text)
    vec_derby = embedder.embed_and_score(derby_text)

    for v in [vec_title, vec_relegation, vec_derby]:
        assert "title_race" in v
        assert "derby_rivalry" in v
        assert "relegation_scrap" in v
        assert "attacking_chaos" in v
        for val in v.values():
            assert 0.0 <= val <= 1.0

    # Comprobar discriminación de ejes
    assert vec_title["title_race"] > vec_title["relegation_scrap"]
    assert vec_relegation["relegation_scrap"] > vec_relegation["title_race"]
    assert vec_derby["derby_rivalry"] > vec_derby["relegation_scrap"]


def test_nlp_feature_extractor_full_phase2():
    title_fix, _, _ = _sample_fixtures()
    extractor = NLPFeatureExtractor()

    narrative_data = {
        "headlines": ["Manchester City vs Arsenal: Monumental Premier League title decider"],
        "fan_comments": ["Incredible excitement, epic game of the season, pure fireworks!"],
        "media_articles_count": 130
    }

    feat = extractor.extract(title_fix, narrative_data)

    assert 0.0 <= feat.fan_excitement_index <= 100.0
    assert -1.0 <= feat.sentiment_compound <= 1.0
    assert 0.0 <= feat.media_velocity <= 100.0
    assert 0.0 <= feat.narrative_rivalry_score <= 1.0
    assert 0.0 <= feat.dramatic_intensity_score <= 1.0
    assert 0.0 <= feat.normalized_nlp_score <= 100.0
    assert feat.comments_volume > 0
    assert feat.comment_velocity_per_min >= 0.0
    assert len(feat.trending_keywords) > 0
    assert "title_race" in feat.context_relevance_vector
