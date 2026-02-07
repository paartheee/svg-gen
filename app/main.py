from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import generate, edit

app = FastAPI(title="Semantic SVG Editor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_config": {"pro": settings.GEMINI_PRO_MODEL}}

app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(edit.router, prefix="/api", tags=["edit"])
