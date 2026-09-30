from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.core.schemas import Team, Fixture


class BaseDataProvider(ABC):
    @abstractmethod
    def get_teams(self) -> List[Team]:
        """Obtiene la lista de los 20 equipos con sus estadísticas."""
        pass

    @abstractmethod
    def get_fixtures(self, gameweek: Optional[int] = None, date: Optional[str] = None) -> List[Fixture]:
        """Obtiene el listado de partidos de una jornada y/o fecha específica (YYYY-MM-DD)."""
        pass

    @abstractmethod
    def get_narratives(self, fixture_id: int) -> Dict[str, Any]:
        """Obtiene titulares, comentarios y volumen mediático para un partido."""
        pass
