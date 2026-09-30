import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.core.config import settings
from src.core.schemas import Team, Fixture
from src.data_ingestion.base import BaseDataProvider


class LocalDataProvider(BaseDataProvider):
    """Proveedor de datos locales basado en archivos JSON pregenerados."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.data_dir
        self._teams_cache: Optional[Dict[int, Team]] = None
        self._fixtures_cache: Optional[List[dict]] = None
        self._narratives_cache: Optional[Dict[str, Any]] = None

    def _load_teams(self) -> Dict[int, Team]:
        if self._teams_cache is None:
            teams_file = self.data_dir / "sample_teams.json"
            with open(teams_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._teams_cache = {item["id"]: Team(**item) for item in data}
        return self._teams_cache

    def _load_fixtures_raw(self) -> List[dict]:
        if self._fixtures_cache is None:
            fixtures_file = self.data_dir / "sample_fixtures.json"
            with open(fixtures_file, "r", encoding="utf-8") as f:
                self._fixtures_cache = json.load(f)
        return self._fixtures_cache

    def _load_narratives(self) -> Dict[str, Any]:
        if self._narratives_cache is None:
            narratives_file = self.data_dir / "sample_narratives.json"
            with open(narratives_file, "r", encoding="utf-8") as f:
                self._narratives_cache = json.load(f)
        return self._narratives_cache

    def get_teams(self) -> List[Team]:
        teams_dict = self._load_teams()
        return list(teams_dict.values())

    def get_fixtures(self, gameweek: Optional[int] = None, date: Optional[str] = None) -> List[Fixture]:
        teams_dict = self._load_teams()
        raw_fixtures = self._load_fixtures_raw()
        
        fixtures: List[Fixture] = []
        for raw in raw_fixtures:
            if gameweek is not None and raw["gameweek"] != gameweek:
                continue
            if date is not None and not raw.get("kickoff_time", "").startswith(date):
                continue
            home_team = teams_dict[raw["home_team_id"]]
            away_team = teams_dict[raw["away_team_id"]]
            fixture = Fixture(
                id=raw["id"],
                gameweek=raw["gameweek"],
                home_team=home_team,
                away_team=away_team,
                kickoff_time=raw["kickoff_time"],
                is_derby=raw.get("is_derby", False),
                derby_name=raw.get("derby_name"),
            )
            fixtures.append(fixture)
        return fixtures

    def get_narratives(self, fixture_id: int) -> Dict[str, Any]:
        narratives = self._load_narratives()
        str_id = str(fixture_id)
        if str_id in narratives:
            return narratives[str_id]
        
        # Fallback genérico si no se encuentra
        return {
            "headlines": ["Premier League fixture showdown"],
            "fan_comments": ["Looking forward to this match!"],
            "media_articles_count": 10,
        }
