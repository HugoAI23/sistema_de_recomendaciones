import math
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class CommentaryDramaClassifier:
    """Clasificador de Dramatismo Narrativo basado en textos de narración minuto a minuto
    y previas periodísticas. Evalúa la probabilidad de desenlaces épicos, remontadas y partidos dinámicos."""

    # Corpus sintético representativo de partidos históricos de alto dramatismo vs partidos rutinarios
    TRAINING_SAMPLES = [
        # Alto dramatismo (Etiqueta 1)
        ("Incredible stoppage time winner! Unbelievable scenes as dramatic comeback stuns rivals in the 94th minute", 1),
        ("Pure madness and chaos! Red card, penalty drama and furious touchline brawl in epic derby showdown", 1),
        ("Frenetic end-to-end thriller with relentless attacking fireworks and defensive collapse on both sides", 1),
        ("Stunning turnaround from two goals down! Last-gasp equalizer sends the stadium into absolute delirium", 1),
        ("High stakes dogfight filled with hostile tackles, heart-stopping saves and boiling tension", 1),
        ("Agonising late drama! Stoppage time controversy and dramatic penalty save keeps survival hopes alive", 1),
        ("Rollercoaster match of pure chaos, five goals and non-stop action from the first whistle", 1),
        # Bajo dramatismo / Rutinarios (Etiqueta 0)
        ("Routine comfortable victory with solid defensive shape and slow tempo throughout the ninety minutes", 0),
        ("Cautious scoreless stalemate with few clear chances and methodical midfield possession battle", 0),
        ("Disciplined professional performance, controlled possession and uneventful second half procession", 0),
        ("Low-tempo encounter with both teams settling for a safe point in quiet afternoon affair", 0),
        ("Flat and quiet match with limited ambition, standard fouls and no significant penalty area action", 0),
        ("Predictable one-sided contest where the favorite cruised to three points without breaking sweat", 0),
    ]

    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.model = LogisticRegression(C=1.5, solver="lbfgs")
        self._is_trained = False
        self._train()

    def _train(self):
        samples = list(self.TRAINING_SAMPLES)
        # Cargar datos de entrenamiento de la temporada actual 2026-2027 si existen
        try:
            import json
            from src.core.config import settings
            matches_file = settings.data_dir / "season_2026_2027_matches.json"
            if matches_file.exists():
                with open(matches_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    text = item.get("commentary_sample")
                    if text:
                        label = 1 if item.get("dramatic_intensity_score", 0.5) >= 0.70 else 0
                        samples.append((text, label))
        except Exception:
            pass

        texts, labels = zip(*samples)
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self._is_trained = True

    def predict_drama_score(
        self,
        full_text: str,
        is_derby: bool = False,
        table_diff: int = 10,
    ) -> float:
        """Calcula la probabilidad de dramatismo continuo en el rango [0.0, 1.0]."""
        if not full_text.strip():
            base_score = 0.5
        else:
            try:
                x_vec = self.vectorizer.transform([full_text])
                prob_high_drama = float(self.model.predict_proba(x_vec)[0][1])
                base_score = prob_high_drama
            except Exception:
                base_score = 0.5

        # Moduladores contextuales de dramatismo
        # 1. Bono por derbi histórico (+0.15)
        if is_derby:
            base_score += 0.15

        # 2. Bono por choque directo en la tabla (cercanía = mayor angustia deportiva)
        if table_diff <= 2:
            base_score += 0.08
        elif table_diff <= 4:
            base_score += 0.04

        final_drama = round(min(1.0, max(0.05, base_score)), 3)
        return final_drama
