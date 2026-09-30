# Premier League Match Recommender
## Especificación de Arquitectura Híbrida: Procesamiento de Lenguaje Natural (PLN) + Analítica Numérica

---

## 1. Resumen Ejecutivo y Visión del Sistema

A diferencia de las plataformas estáticas de streaming (como Netflix), recomendar eventos deportivos en vivo o partidos futuros de la **Premier League** requiere evaluar el **potencial de espectáculo ($Excitement\ Score$)** antes de que ocurra el evento. 

Este proyecto propone un motor de recomendación híbrido y multimodal que combina:
1. **Métricas estadísticas objetivas**: Goles Esperados ($xG$), posición en la tabla de clasificación, paridad competitiva e intensidad táctica.
2. **Señales cualitativas en tiempo real**: Sentimiento de la afición en comunidades como Reddit, cobertura mediática y narrativas periodísticas procesadas mediante Procesamiento del Lenguaje Natural (PLN).

---

## 2. Diagrama de Arquitectura Multimodal

```
+-----------------------------------------------------------------------+
|                         FUENTES DE DATOS                              |
|                                                                       |
|  [CSVs Históricos (5-10 Yrs)]            [APIs en Tiempo Real]        |
|  - Football-Data.co.uk                   - Reddit API (PRAW)          |
|  - FBref / Understat                     - API-Football (RapidAPI)    |
|  - ESPN Commentary Datasets              - Official FPL API           |
|  - FPL Historical Data                   - News API / GNews           |
+-------------------+-----------------------------------+---------------+
                    |                                   |
                    v                                   v
+-------------------+-----------------------------------+---------------+
|                   PIPELINES DE EXTRACCIÓN Y FEATURE ENG.              |
|                                                                       |
|  [Pipeline Numérico & Táctico]          [Pipeline PLN / NLP]          |
|  - Combined Expected Goals (xG)         - VADER Sentiment Analysis    |
|  - Paridad en Tabla & Forma             - Sentence-Transformers       |
|  - ICT Star Player Availability         - Commentary Intensity Model  |
+-------------------+-----------------------------------+---------------+
                    |                                   |
                    +-----------------+-----------------+
                                      |
                                      v
+-------------------------------------+---------------------------------+
|                        MOTOR HÍBRIDO (ML SCORING)                     |
|                                                                       |
|        Score = w1(xG) + w2(Paridad) + w3(Sentiment) + w4(Media)      |
+-------------------------------------+---------------------------------+
                                      |
                                      v
+-------------------------------------+---------------------------------+
|                    SISTEMA DE RECOMENDACIÓN & SERVING                 |
|                                                                       |
|  - REST API (FastAPI)                                                 |
|  - Top 3 Partidos Recomendados + Justificación Semántica             |
+-----------------------------------------------------------------------+
```

---

## 3. Catálogo de Archivos Dataset (CSVs Históricos)

Estos archivos permiten entrenar los modelos base offline de probabilidad de eventos, volatilidad y clasificación de dramatismo narrativo.

| Archivo CSV | Fuente de Origen | Variables Contenidas | Propósito en el Recomendador |
| :--- | :--- | :--- | :--- |
| `EPL_Matches_10Y.csv` | Football-Data.co.uk | Goles, tiros al arco, córners, faltas, tarjetas, odds de apuestas. | Entrenar el modelo base de probabilidad de goles y volatilidad del partido. |
| `EPL_Advanced_Stats.csv` | FBref (vía `soccerdata`) | Goles Esperados ($xG$), $xGA$, pases progresivos, presión alta, SCA. | Definir el perfil táctico e intensidad de juego de cada club. |
| `EPL_Commentaries.csv` | Kaggle / ESPN | Narración textual minuto a minuto de partidos históricos. | Entrenar clasificadores NLP para calificar "Partidos Dramáticos". |
| `EPL_FPL_Historical.csv` | Fantasy Premier League API | Índice ICT (*Influence, Creativity, Threat*), puntos por partido. | Medir la relevancia y nivel de forma individual de los jugadores estrella. |

---

## 4. Integración de APIs en Tiempo Real

Para evaluar los partidos de la jornada próxima o en curso, el sistema consume cuatro APIs clave:

| API Service | Endpoints / Métodos | Información Extraída | Frecuencia de Consulta |
| :--- | :--- | :--- | :--- |
| **API-Football** *(RapidAPI)* | `/fixtures`, `/standings`, `/lineups` | Calendario oficial, tabla de posiciones, alineaciones confirmadas, lesionados. | Diaria / Cada 15 min en jornada |
| **Reddit API** *(PRAW)* | `r/soccer`, `r/PremierLeague` | Hilos *Pre-Match* y *Match Threads*: volumen de comentarios, karma y velocidad. | En tiempo real (cada 30 min) |
| **Official FPL API** | `/bootstrap-static/`, `/element-summary/` | Popularidad de jugadores (% de selección), estado físico e índice ICT. | Semanal / Pre-jornada |
| **News API / GNews** | `/v2/everything` | Noticias pre-partido, declaraciones de entrenadores y tensión por derbis. | Diario |

---

## 5. Arquitectura del Pipeline de PLN (Procesamiento de Lenguaje Natural)

El módulo de PLN transforma texto no estructurado en métricas cuantitativas para el recomendador:

1. **Análisis de Sentimiento y Hype (Reddit)**:
   - Se utiliza **NLTK VADER** o **RoBERTa** para analizar los hilos de conversación previos.
   - Se extrae la densidad de comentarios por minuto y la carga emocional de los aficionados.
2. **Embeddings de Narrativas Tácticas**:
   - Usando **Sentence-Transformers** (`all-MiniLM-L6-v2`), convertimos artículos y previas de prensa en vectores contextuales.
   - Detecta temáticas clave como *"lucha por el título"*, *"zona de descenso"* o *"derbi histórico"*.
3. **Clasificador de Dramatismo Narrativo**:
   - Algoritmo entrenado con minutos a minuto pasados para predecir si la narrativa entre dos equipos tiende a generar un fútbol dinámico ("ida y vuelta", "remontada agónica").
4. **Aceleración Mediática (*Media Velocity*)**:
   - Mide el incremento inusual de noticias respecto al promedio de la temporada para capturar eventos de alto impacto nacional.

### Algoritmos y Modelos PLN Seleccionados

| Técnica PLN | Librería / Modelo Base | Entrada de Texto | Métrica Generada |
| :--- | :--- | :--- | :--- |
| **Análisis de Polaridad** | `NLTK VADER` / `TextBlob` | Comentarios en Reddit | `Fan_Excitement_Index` ($0-100$) |
| **Embeddings Semánticos** | `all-MiniLM-L6-v2` | Titulares y previas de prensa | `Context_Relevance_Vector` |
| **TF-IDF + Cosine Similarity** | `scikit-learn` | Histórico narrativo | `Derby_Rivalry_Score` ($0-1$) |

---

## 6. Métricas Numéricas y Tácticas

Paralelamente, se calculan variables numéricas para evaluar la calidad futbolística esperada:

* **Combined Expected Goals ($xG_{comb}$)**:
  $$xG_{comb} = xG_{Local} + xG_{Visitante}$$
  *(Promedio de los últimos 5 partidos de cada club).*
* **Índice de Paridad en la Tabla ($Paridad$)**:
  $$Paridad = 1 - \frac{|Pos_{Local} - Pos_{Visitante}|}{20}$$
* **Disponibilidad de Jugadores Estrella ($Star\ Power$)**:
  $$Star\ Power = \sum_{i \in Titulares} ICT\_Index_i$$

---

## 7. Formulación Matemática del Modelo de Scoring

El algoritmo unifica las fuentes cuantitativas y cualitativas mediante una función objetivo ponderada:

$$Score_{partido} = w_1 \cdot xG_{comb} + w_2 \cdot Paridad + w_3 \cdot Fan\_Excitement\_Index + w_4 \cdot Media\_Velocity$$

Donde $\sum_{i=1}^{4} w_i = 1.0$. Los pesos se ajustan según la preferencia del usuario (ej. priorizar partidos de alto espectáculo vs. partidos de alta tensión táctica).

---

## 8. Stack Tecnológico de Librerías en Python

```python
# Extracción de Datos
import requests
import praw          # Reddit API Wrapper
import soccerdata    # Extracción automática de FBref/Understat
import understat

# Procesamiento de Lenguaje Natural (PLN)
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy
from sentence_transformers import SentenceTransformer

# Análisis de Datos y Machine Learning
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import xgboost as xgb

# Backend & Serving
from fastapi import FastAPI
import uvicorn
```

---

## 9. Plan de Implementación (Roadmap)

- [x] **Fase 1: Ingesta de Datos**: Configuración de credenciales de API (PRAW, API-Football) y descarga/proveedores de datasets (`Football-Data`, `FBref`, `FPL Public API` y fallback offline).
- [x] **Fase 2: Pipeline de PLN**: Desarrollo de módulos para extracción e interpretación de afición en Reddit (VADER), cobertura mediática, clasificador de dramatismo en comentarios y embeddings semánticos multieje (`title_race`, `derby_rivalry`, `relegation_scrap`, `attacking_chaos`).
- [x] **Fase 3: Integración del Motor Híbrido**: Unificación de variables numéricas ($xG$, paridad, *Star Power*, estilo táctico operativo $Similitud(Pases_{Progresivos}, Presiones)$) con señales de PLN. Ajuste matemático de pesos ($w_1, w_2, w_3, w_4$) mediante validación cruzada ($k$-Fold CV, Spearman=0.963, NDCG@3=0.998) y motor de scoring de Machine Learning (`GradientBoostingRegressor`).
- [x] **Fase 4: Desarrollo de la API REST**: Endpoints finales (GET/POST con soporte para fechas y jornadas) y panel interactivo web (Dashboard en `/dashboard`) para servir el Top 3 de partidos recomendados de la jornada junto con explicaciones generadas automáticamente y telemetría de validación cruzada.