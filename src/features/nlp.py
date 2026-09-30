from typing import Dict, Any, List, Optional
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.core.config import settings
from src.core.schemas import Fixture, MatchNLPFeatures
from src.features.commentary_classifier import CommentaryDramaClassifier
from src.data_ingestion.reddit_extractor import RedditNarrativeExtractor
from src.data_ingestion.news_extractor import NewsNarrativeExtractor

# Asegurar ruta local de nltk_data
if str(settings.nltk_data_dir) not in nltk.data.path:
    nltk.data.path.insert(0, str(settings.nltk_data_dir))

from nltk.sentiment.vader import SentimentIntensityAnalyzer


class ContextSemanticEmbedder:
    """Embedder semántico modular para clasificar la narrativa del partido en 4 ejes clave:
    - title_race: Lucha por el título o cima de la tabla.
    - derby_rivalry: Derbi local y rivalidad apasionada.
    - relegation_scrap: Batalla por la permanencia y zona de descenso.
    - attacking_chaos: Encuentro dinámico de ida y vuelta con alto potencial goleador.
    
    Implementa un patrón híbrido: Modo ligero instantáneo (TF-IDF + Cosine) por defecto,
    o Sentence-Transformers (all-MiniLM-L6-v2) si está activado y disponible."""

    NARRATIVE_AXES = {
        "title_race": "massive title showdown title decider championship first place epic top clash summit race leaders",
        "derby_rivalry": "fierce local derby hostile rivalry hatred intense tackles electric atmosphere bragging rights bad blood pride",
        "relegation_scrap": "relegation dogfight survival six pointer drop zone desperate fight chaos drama scrap bottom danger",
        "attacking_chaos": "thriller relentless attacking fireworks open game pure madness end to end goals slugfest offensive frenzy",
    }

    def __init__(self, use_transformers: bool = False):
        self.use_transformers = use_transformers or settings.use_sentence_transformers
        self._st_model = None
        self._axis_embeddings = {}

        if self.use_transformers:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
                for axis, text in self.NARRATIVE_AXES.items():
                    self._axis_embeddings[axis] = self._st_model.encode([text])
            except Exception:
                self._st_model = None

        # Modelo TF-IDF de alta fidelidad como motor base ligero y de coste cero
        self.tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        axis_texts = list(self.NARRATIVE_AXES.values())
        self.axis_keys = list(self.NARRATIVE_AXES.keys())
        self.tfidf_reference_matrix = self.tfidf.fit_transform(axis_texts)

    def embed_and_score(self, text: str) -> Dict[str, float]:
        """Calcula el vector de afinidad contextual [0.0 - 1.0] para cada uno de los 4 ejes narrativos."""
        if not text.strip():
            return {k: 0.1 for k in self.NARRATIVE_AXES}

        # 1. Modo Transformers si está habilitado
        if self._st_model is not None:
            try:
                text_emb = self._st_model.encode([text])
                vector: Dict[str, float] = {}
                for axis, emb in self._axis_embeddings.items():
                    sim = float(cosine_similarity(text_emb, emb)[0][0])
                    vector[axis] = round(max(0.0, min(1.0, sim)), 3)
                return vector
            except Exception:
                pass

        # 2. Modo TF-IDF Zero-Cost (Ligero, rápido y determinista)
        try:
            doc_vec = self.tfidf.transform([text])
            sims = cosine_similarity(doc_vec, self.tfidf_reference_matrix)[0]
            vector = {}
            for idx, key in enumerate(self.axis_keys):
                vector[key] = round(float(max(0.0, min(1.0, sims[idx]))), 3)
            return vector
        except Exception:
            return {k: 0.2 for k in self.NARRATIVE_AXES}


class NLPFeatureExtractor:
    """Extractor integral de métricas cualitativas y de Procesamiento de Lenguaje Natural (PLN) para partidos."""

    def __init__(
        self,
        reddit_extractor: Optional[RedditNarrativeExtractor] = None,
        news_extractor: Optional[NewsNarrativeExtractor] = None,
        drama_classifier: Optional[CommentaryDramaClassifier] = None,
        embedder: Optional[ContextSemanticEmbedder] = None,
    ):
        self.sia = SentimentIntensityAnalyzer()
        self.reddit_extractor = reddit_extractor or RedditNarrativeExtractor()
        self.news_extractor = news_extractor or NewsNarrativeExtractor()
        self.drama_classifier = drama_classifier or CommentaryDramaClassifier()
        self.embedder = embedder or ContextSemanticEmbedder()

    def extract(self, fixture: Fixture, narrative_data: Dict[str, Any]) -> MatchNLPFeatures:
        # Extraer o enriquecer datos de Reddit y Prensa
        seed_headlines = narrative_data.get("headlines", [])
        seed_comments = narrative_data.get("fan_comments", [])
        raw_article_count = narrative_data.get("media_articles_count")

        reddit_info = self.reddit_extractor.extract_fixture_discussion(fixture, seed_comments)
        news_info = self.news_extractor.extract_fixture_news(fixture, seed_headlines, raw_article_count)

        fan_comments = reddit_info["fan_comments"]
        headlines = news_info["headlines"]
        comments_count = reddit_info.get("comments_count", len(fan_comments) * 50)
        comment_velocity = reddit_info.get("comment_velocity", 2.0)
        media_count = news_info.get("media_articles_count", 20)

        all_texts = headlines + fan_comments
        full_text = " ".join(all_texts) if all_texts else f"{fixture.home_team.name} vs {fixture.away_team.name} preview"

        # 1. Análisis de Sentimiento y Hype (Reddit) con NLTK VADER
        sentiment_scores = [self.sia.polarity_scores(t)["compound"] for t in all_texts] if all_texts else [0.0]
        avg_compound = float(sum(sentiment_scores) / max(1, len(sentiment_scores)))

        # En fútbol la expectativa (hype) combina polaridad positiva, carga emocional intensa y velocidad de comentarios
        base_sentiment = ((avg_compound + 1.0) / 2.0) * 50.0       # [0 - 50]
        emotional_intensity = abs(avg_compound) * 30.0             # [0 - 30]
        velocity_boost = min(20.0, (comment_velocity / 6.0) * 20.0) # [0 - 20]
        
        fan_excitement_index = min(100.0, max(10.0, base_sentiment + emotional_intensity + velocity_boost))
        if fixture.is_derby:
            fan_excitement_index = min(100.0, fan_excitement_index + 10.0)

        # 2. Aceleración Mediática (Media Velocity) [0 - 100]
        media_velocity = min(100.0, max(5.0, (media_count / 120.0) * 100.0))

        # 3. Vector de Relevancia Contextual (Embeddings Semánticos de 4 ejes)
        context_vector = self.embedder.embed_and_score(full_text)
        narrative_rivalry_score = context_vector.get("derby_rivalry", 0.2)
        if fixture.is_derby:
            narrative_rivalry_score = min(1.0, narrative_rivalry_score + 0.25)
            context_vector["derby_rivalry"] = round(narrative_rivalry_score, 3)

        # 4. Clasificador de Dramatismo Narrativo
        table_diff = abs(fixture.home_team.position - fixture.away_team.position)
        dramatic_score = self.drama_classifier.predict_drama_score(
            full_text=full_text,
            is_derby=fixture.is_derby,
            table_diff=table_diff
        )

        # 5. Extracción de Trending Keywords con CountVectorizer
        try:
            count_vec = CountVectorizer(stop_words="english", max_features=5)
            count_vec.fit([full_text])
            trending_keywords = list(count_vec.vocabulary_.keys())
        except Exception:
            trending_keywords = ["premierleague", "matchday"]

        # 6. Score PLN Compuesto Normalizado [0 - 100]
        # Ponderación equilibrada:
        # 35% Fan Excitement + 25% Media Velocity + 20% Rivalidad/Narrativa + 20% Dramatismo
        normalized_nlp = round(
            (0.35 * fan_excitement_index) +
            (0.25 * media_velocity) +
            (0.20 * (narrative_rivalry_score * 100.0)) +
            (0.20 * (dramatic_score * 100.0)),
            2
        )
        normalized_nlp = min(100.0, max(0.0, normalized_nlp))

        return MatchNLPFeatures(
            fixture_id=fixture.id,
            fan_excitement_index=round(fan_excitement_index, 2),
            sentiment_compound=round(avg_compound, 3),
            media_velocity=round(media_velocity, 2),
            narrative_rivalry_score=round(narrative_rivalry_score, 3),
            context_relevance_vector=context_vector,
            dramatic_intensity_score=round(dramatic_score, 3),
            comments_volume=comments_count,
            comment_velocity_per_min=round(comment_velocity, 2),
            trending_keywords=trending_keywords,
            sample_headlines=headlines[:2],
            normalized_nlp_score=normalized_nlp,
        )
