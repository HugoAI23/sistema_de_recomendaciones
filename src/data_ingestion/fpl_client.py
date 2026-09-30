import requests
from typing import List, Optional, Dict, Any
from src.core.config import settings
from src.core.schemas import Team, Fixture
from src.data_ingestion.base import BaseDataProvider
from src.data_ingestion.local_provider import LocalDataProvider


class FPLDataProvider(BaseDataProvider):
    """Proveedor que consulta la API pública y gratuita de Fantasy Premier League (FPL).
    Si la conexión falla o no hay red, realiza fallback automático a LocalDataProvider."""

    def __init__(self, fallback_provider: Optional[BaseDataProvider] = None):
        self.base_url = settings.fpl_base_url
        self.fallback = fallback_provider or LocalDataProvider()
        self._cached_teams: Optional[List[Team]] = None
        self._cached_fixtures: Optional[List[Fixture]] = None

    def get_teams(self) -> List[Team]:
        if self._cached_teams is not None:
            return self._cached_teams

        url = f"{self.base_url}/bootstrap-static/"
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                raw_teams = data.get("teams", [])
                teams: List[Team] = []
                for t in raw_teams:
                    # En FPL strength / form da señal táctica
                    team = Team(
                        id=t["id"],
                        name=t["name"],
                        short_name=t["short_name"],
                        position=t.get("position", 10),
                        points=t.get("points", 40),
                        played=t.get("played", 28),
                        xg_for_last5=float(t.get("strength_attack_home", 1200)) / 700.0,
                        xga_for_last5=float(t.get("strength_defence_away", 1200)) / 900.0,
                        form="WWDLW",
                        key_players_ict=float(t.get("strength", 3)) * 70.0,
                        rivals=[]
                    )
                    teams.append(team)
                if teams:
                    self._cached_teams = teams
                    return teams
        except Exception:
            pass

        # Fallback a datos locales
        self._cached_teams = self.fallback.get_teams()
        return self._cached_teams

    def get_fixtures(self, gameweek: Optional[int] = None, date: Optional[str] = None) -> List[Fixture]:
        if self._cached_fixtures is not None:
            fixtures = self._cached_fixtures
            if gameweek is not None:
                fixtures = [f for f in fixtures if f.gameweek == gameweek]
            if date is not None:
                fixtures = [f for f in fixtures if f.kickoff_time.startswith(date)]
            return fixtures

        url = f"{self.base_url}/fixtures/"
        try:
            params = {}
            if gameweek:
                params["event"] = gameweek
            resp = requests.get(url, params=params, timeout=4)
            if resp.status_code == 200:
                raw_fixtures = resp.json()
                teams = {t.id: t for t in self.get_teams()}
                fixtures: List[Fixture] = []
                for rf in raw_fixtures:
                    if rf.get("finished", False):
                        continue
                    home_id = rf.get("team_h")
                    away_id = rf.get("team_a")
                    if home_id in teams and away_id in teams:
                        f = Fixture(
                            id=rf.get("id"),
                            gameweek=rf.get("event") or (gameweek or 1),
                            home_team=teams[home_id],
                            away_team=teams[away_id],
                            kickoff_time=rf.get("kickoff_time", "2026-04-01T15:00:00Z"),
                            is_derby=False,
                            derby_name=None
                        )
                        fixtures.append(f)
                if fixtures:
                    self._cached_fixtures = fixtures
                    result = fixtures
                    if gameweek is not None:
                        result = [f for f in result if f.gameweek == gameweek]
                    if date is not None:
                        result = [f for f in result if f.kickoff_time.startswith(date)]
                    return result
        except Exception:
            pass

        # Fallback a datos locales
        all_fixtures = self.fallback.get_fixtures()
        self._cached_fixtures = all_fixtures
        result = all_fixtures
        if gameweek is not None:
            result = [f for f in result if f.gameweek == gameweek]
        if date is not None:
            result = [f for f in result if f.kickoff_time.startswith(date)]
        return result

    def get_narratives(self, fixture_id: int) -> Dict[str, Any]:
        return self.fallback.get_narratives(fixture_id)
