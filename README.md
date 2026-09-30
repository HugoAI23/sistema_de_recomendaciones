# Premier League Match Recommender (MVP)

Motor de recomendación híbrido y multimodal para partidos de la Premier League basado en la metodología **SDD (Schema-Driven Development)** y una **estrategia de datos de coste cero (Zero-Cost Data Strategy)**.

---

## 🎯 ¿Qué problema resuelve?
A diferencia de sistemas de recomendación tradicionales, evaluar partidos de fútbol en vivo o futuros requiere predecir el **potencial de espectáculo (*Excitement Score*)** antes del pitazo inicial.

El sistema fusiona dos mundos:
1. **Analítica Numérica Objetiva**: Goles Esperados combinados ($xG_{comb}$), paridad en la tabla clasificatoria y presencia de estrellas (*Star Power* ICT).
2. **Procesamiento de Lenguaje Natural (PLN)**: Expectativa de la afición (*Fan Excitement Index* con VADER Sentiment), velocidad de cobertura mediática (*Media Velocity*) y detección de rivalidades/derbis con TF-IDF y similitud de coseno.

---

## 🏗️ Arquitectura por Fases (SDD)

```
[Fuentes Gratuitas / Local Seed] 
       │
       ├──► [Pipeline Numérico: xG, Paridad, Star Power] ────┐
       │                                                     ▼
       └──► [Pipeline PLN: VADER, Hype, TF-IDF Rivalidad] ──► [Motor de Scoring Híbrido]
                                                                     │
                                                             [Ranking Top 3 + Justificaciones]
                                                                     │
                                                             ┌───────┴───────┐
                                                             ▼               ▼
                                                       [FastAPI REST]    [CLI Demo]
```

---

## 🚀 Puesta en Marcha Rápida

### 1. Requisitos
- Python 3.10+
- Entorno virtual activado

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Probar mediante CLI (Línea de Comandos)
Puedes ejecutar recomendaciones inmediatas directamente en la terminal:

```bash
# Perfil optimizado matemáticamente por Validación Cruzada k-Fold (por defecto)
python -m src.cli --top 3

# Filtrar por fecha específica de la jornada (Fase 4)
python -m src.cli --date 2026-03-31 --top 2

# Modo de inferencia avanzada con Machine Learning (Gradient Boosting)
python -m src.cli --model ml_hybrid --top 3

# Reporte de métricas de validación cruzada y pesos calibrados
python -m src.cli --cv-report

# Perfiles específicos por estilo de aficionado
python -m src.cli --profile tension --top 3
python -m src.cli --profile goal_fest --top 3
```

### 3. Levantar la API REST y el Panel Web Interactivo (FastAPI)
Por defecto, el servicio se ejecuta en el puerto **`8080`** (evitando colisiones con otros proyectos locales):

```bash
# Opción 1: Ejecutar directamente el módulo
python -m src.api.app

# Opción 2: Con uvicorn CLI explícito
python -m uvicorn src.api.app:app --reload --port 8080
```

> [!TIP]
> Puedes cambiar el puerto en cualquier momento definiendo la variable de entorno `API_PORT` (ej: `API_PORT=8090 python -m src.api.app`).

- **🖥️ Panel Web Interactivo (Dashboard Fase 4)**: Abre en el navegador `http://localhost:8080/dashboard` o `http://localhost:8080/`
- **Documentación Interactiva (Swagger UI)**: Abre `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### 4. Ejecutar la Batería de Pruebas Automatizadas
```bash
pytest -v
```

### 5. Explorar los Notebooks Interactivos (Tratamiento de Datos y Modelado por Fase)
En la carpeta [`notebooks/`](file:///Users/hugoportillo/sistema_de_recomendaciones/notebooks) se encuentran los Jupyter Notebooks con la ejecución paso a paso:
1. **[01_fase1_tratamiento_datos_ingesta.ipynb](file:///Users/hugoportillo/sistema_de_recomendaciones/notebooks/01_fase1_tratamiento_datos_ingesta.ipynb)**: Ingesta, validación Pydantic, limpieza y análisis exploratorio (EDA) de los 20 clubes y calendario.
2. **[02_fase2_pln_tratamiento_narrativas_y_dramatismo.ipynb](file:///Users/hugoportillo/sistema_de_recomendaciones/notebooks/02_fase2_pln_tratamiento_narrativas_y_dramatismo.ipynb)**: Preprocesamiento de texto, sentimiento con VADER, embeddings semánticos multieje y **entrenamiento del clasificador de dramatismo narrativo** (`LogisticRegression`).
3. **[03_fase3_tratamiento_numerico_y_entrenamiento_modelo_hibrido.ipynb](file:///Users/hugoportillo/sistema_de_recomendaciones/notebooks/03_fase3_tratamiento_numerico_y_entrenamiento_modelo_hibrido.ipynb)**: Choque táctico operativo, **optimización matemática de pesos por Validación Cruzada ($k$-Fold CV)** y **entrenamiento del modelo de Machine Learning supervisado** (`GradientBoostingRegressor`).
4. **[04_fase4_serving_evaluacion_y_recomendaciones.ipynb](file:///Users/hugoportillo/sistema_de_recomendaciones/notebooks/04_fase4_serving_evaluacion_y_recomendaciones.ipynb)**: Inferencia end-to-end, Top 3 recomendado, explicaciones semánticas estructuradas, benchmarking de perfiles y simulación de la API REST.

---

## 📡 Endpoints de la API REST (Fase 4)

| Método | Endpoint | Parámetros Clave | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/` y `/dashboard` | — | **(Fase 4)** Panel web interactivo con interfaz oficial estilo Premier League, sliders en tiempo real y modal de telemetría. |
| `GET` | `/api/v1/health` | — | Estado del microservicio, modo de coste cero y fase completada (`Fase 4: API REST & Panel Interactivo`). |
| `GET` | `/api/v1/dashboard` | — | Endpoint API para servir la interfaz web del dashboard. |
| `GET` | `/api/v1/profiles` | — | Perfiles de ponderación (`cv_optimal`, `balanced`, `goal_fest`, `tension`, `fan_hype`). |
| `GET` | `/api/v1/teams` | — | Tabla de posiciones y métricas de los 20 clubes. |
| `GET` | `/api/v1/fixtures` | `?gameweek=29&date=2026-03-31` | Lista los partidos disponibles con soporte de filtrado por jornada y fecha. |
| `GET` | `/api/v1/recommendations/top3` | `?gameweek=29&date=2026-03-31&profile=cv_optimal&model_type=ml_hybrid&top_n=3` | **(Fase 4)** Retorna el Top N de partidos recomendados vía query string. |
| `POST` | `/api/v1/recommendations/top3` | Body JSON (`gameweek`, `date`, `profile`, `custom_weights`, `model_type`, `top_n`) | Retorna los 3 mejores partidos con justificantes semánticos y desglose de pesos. |
| `GET` | `/api/v1/fixtures/{id}/analysis` | `?profile=balanced&model_type=weighted` | Análisis desglosado cuantitativo, táctico y PLN para un partido particular. |
| `GET` | `/api/v1/hybrid/cross-validation` | — | Telemetría de validación cruzada $k$-Fold, pesos óptimos e importancia de variables del modelo ML. |

---

## ⚖️ Formulación Matemática y Validación Cruzada (Fase 3)

### 1. Modelo de Scoring Canónico Ponderado
$$Score_{partido} = w_1 \cdot xG_{comb} + w_2 \cdot Paridad + w_3 \cdot Fan\_Excitement + w_4 \cdot Media\_Velocity$$

Donde $\sum_{i=1}^{4} w_i = 1.0$.

### 2. Calibración Óptima con Validación Cruzada ($k=5$)
Mediante búsqueda en simplex regularizada sobre partidos históricos y arquetípicos de Premier League:
- **Correlación de Ranking Spearman**: **$0.963$**
- **NDCG@3 (Calidad de Ranking Top 3)**: **$0.998$**
- **Error Cuadrático Medio (MSE)**: **$12.67$**
- **Pesos Óptimos Obtenidos (`cv_optimal`)**:
  * $w_{xG} = 0.20$
  * $w_{Paridad} = 0.20$
  * $w_{Fan\_Excitement} = 0.40$
  * $w_{Media\_Velocity} = 0.20$

### 3. Modelo No-Lineal de Machine Learning (`GradientBoostingRegressor`)
Captura interacciones complejas entre el choque táctico operativo ($Similitud(Pases_{Progresivos}, Presiones)$), el dramatismo histórico en comentarios, la afinidad temática contextual y las estrellas en el campo (*Star Power* ICT).

