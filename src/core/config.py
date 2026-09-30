from pathlib import Path
from typing import Dict, Optional
from pydantic_settings import BaseSettings
from src.core.schemas import MatchScoreWeights

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
NLTK_DATA_DIR = PROJECT_ROOT / ".venv" / "share" / "nltk_data"

class Settings(BaseSettings):
    app_name: str = "Premier League Match Recommender API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = 8080
    fpl_base_url: str = "https://fantasy.premierleague.com/api"
    data_dir: Path = DATA_DIR
    nltk_data_dir: Path = NLTK_DATA_DIR

    # Conectores externos para NLP (Opcionales con Zero-Cost fallback automático)
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "PremierLeagueRecommender/1.0"
    news_api_key: Optional[str] = None
    use_sentence_transformers: bool = False

    # Presets de ponderaciones
    weight_profiles: Dict[str, MatchScoreWeights] = {
        "balanced": MatchScoreWeights(w_xg=0.35, w_parity=0.25, w_fan_excitement=0.25, w_media_velocity=0.15),
        "cv_optimal": MatchScoreWeights(w_xg=0.36, w_parity=0.24, w_fan_excitement=0.26, w_media_velocity=0.14),
        "goal_fest": MatchScoreWeights(w_xg=0.60, w_parity=0.10, w_fan_excitement=0.20, w_media_velocity=0.10),
        "tension": MatchScoreWeights(w_xg=0.15, w_parity=0.45, w_fan_excitement=0.25, w_media_velocity=0.15),
        "fan_hype": MatchScoreWeights(w_xg=0.20, w_parity=0.20, w_fan_excitement=0.45, w_media_velocity=0.15),
    }

    # Configuración del Motor Híbrido ML (Fase 3)
    enable_ml_model: bool = True
    default_scoring_mode: str = "weighted"  # "weighted" o "ml_hybrid"

settings = Settings()
