from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.api.routes import router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Premier League Match Recommender API
    Motor de recomendación híbrido y multimodal para partidos de la Premier League.
    Combina analítica numérica (xG, paridad en tabla, forma) con Procesamiento de Lenguaje Natural (VADER Sentiment, Hype, TF-IDF).
    Desarrollado bajo la metodología SDD con arquitectura de coste cero (Zero-Cost Data Strategy).
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Soporte CORS para consumo desde frontends web o móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse
from src.api.dashboard import get_dashboard_html

app.include_router(router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    """Sirve el panel web interactivo principal del Premier League Match Recommender."""
    return HTMLResponse(content=get_dashboard_html(), status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host=settings.api_host, port=settings.api_port, reload=True)
