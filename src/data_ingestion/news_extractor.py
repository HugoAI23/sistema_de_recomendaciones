import logging
from typing import Dict, Any, List, Optional
import requests
from src.core.config import settings
from src.core.schemas import Fixture

logger = logging.getLogger(__name__)


class NewsNarrativeExtractor:
    """Extractor de cobertura mediática, noticias y declaraciones de prensa.
    Soporta NewsAPI / fuentes RSS con fallback offline a datos semilla locales (Zero-Cost)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.news_api_key

    def extract_fixture_news(
        self,
        fixture: Fixture,
        seed_headlines: Optional[List[str]] = None,
        seed_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Obtiene titulares y volumen de artículos publicados para el partido."""
        # 1. Consulta a NewsAPI si existe clave configurada
        if self.api_key:
            try:
                query = f'"{fixture.home_team.name}" AND "{fixture.away_team.name}"'
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": 5,
                    "apiKey": self.api_key,
                }
                resp = requests.get(url, params=params, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = data.get("articles", [])
                    headlines = [a["title"] for a in articles if a.get("title")]
                    total_results = data.get("totalResults", len(headlines))
                    return {
                        "headlines": headlines or seed_headlines or [],
                        "media_articles_count": max(len(headlines), total_results),
                        "is_live": True,
                    }
            except Exception as e:
                logger.debug("Fallo en consulta NewsAPI: %s. Procediendo a fallback.", e)

        # 2. Modo Offline / Fallback
        headlines = seed_headlines or [
            f"{fixture.home_team.name} host {fixture.away_team.name} in crucial Premier League clash",
            f"Tactical preview: key battles as {fixture.home_team.short_name} take on {fixture.away_team.short_name}",
        ]

        if seed_count is not None:
            article_count = seed_count
        else:
            # Estimación sintética según relevancia
            if fixture.is_derby or (fixture.home_team.position <= 3 and fixture.away_team.position <= 3):
                article_count = 110
            elif fixture.home_team.position <= 6 and fixture.away_team.position <= 6:
                article_count = 65
            else:
                article_count = 25

        return {
            "headlines": headlines,
            "media_articles_count": article_count,
            "is_live": False,
        }
