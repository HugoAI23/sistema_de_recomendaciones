import logging
from typing import Dict, Any, List, Optional
from src.core.config import settings
from src.core.schemas import Fixture

logger = logging.getLogger(__name__)


class RedditNarrativeExtractor:
    """Extractor de conversaciones, comentarios y métricas de Hype en Reddit (r/soccer, r/PremierLeague).
    Implementa soporte para PRAW con fallback automático local sin coste (Zero-Cost Strategy)."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        self.client_id = client_id or settings.reddit_client_id
        self.client_secret = client_secret or settings.reddit_client_secret
        self.user_agent = user_agent or settings.reddit_user_agent
        self._reddit = None
        self._initialize_praw()

    def _initialize_praw(self):
        if not self.client_id or not self.client_secret:
            return
        try:
            import praw
            self._reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
        except Exception as e:
            logger.warning("No se pudo inicializar PRAW (%s). Se usará fallback offline.", e)
            self._reddit = None

    def extract_fixture_discussion(
        self,
        fixture: Fixture,
        seed_comments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extrae o sintetiza hilos pre-match y comentarios de afición."""
        # 1. Intento de consulta en vivo vía PRAW si está disponible
        if self._reddit:
            try:
                query = f"{fixture.home_team.name} {fixture.away_team.name} match thread"
                subreddit = self._reddit.subreddit("soccer+PremierLeague")
                submissions = list(subreddit.search(query, sort="relevance", limit=2))
                
                if submissions:
                    top_submission = submissions[0]
                    top_submission.comments.replace_more(limit=0)
                    live_comments = [c.body for c in top_submission.comments[:15] if len(c.body) > 10]
                    num_comments = top_submission.num_comments
                    created_utc = top_submission.created_utc
                    import time
                    elapsed_min = max(1.0, (time.time() - created_utc) / 60.0)
                    velocity = round(num_comments / elapsed_min, 2)

                    return {
                        "fan_comments": live_comments or seed_comments or [],
                        "comments_count": num_comments,
                        "comment_velocity": min(50.0, velocity),
                        "total_karma": top_submission.score,
                        "is_live": True,
                    }
            except Exception as e:
                logger.debug("Fallo en consulta PRAW en vivo: %s. Procediendo a fallback.", e)

        # 2. Modo Offline / Zero-Cost Fallback
        comments = seed_comments or [
            f"Big match incoming between {fixture.home_team.name} and {fixture.away_team.name}!",
            "Can't wait to see how both teams set up tactically.",
            "Massive points on the line this weekend.",
        ]

        is_top_clash = fixture.home_team.position <= 4 and fixture.away_team.position <= 4
        is_derby = fixture.is_derby

        if is_top_clash or is_derby:
            base_count = 1450 if is_top_clash else 980
            base_velocity = 8.5 if is_top_clash else 6.2
            karma = 2100
        elif fixture.home_team.position <= 6 or fixture.away_team.position <= 6:
            base_count = 520
            base_velocity = 3.4
            karma = 650
        else:
            base_count = 210
            base_velocity = 1.2
            karma = 240

        return {
            "fan_comments": comments,
            "comments_count": base_count,
            "comment_velocity": base_velocity,
            "total_karma": karma,
            "is_live": False,
        }
