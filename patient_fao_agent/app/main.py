from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from patient_fao_agent.app.routes import education_routes,voice_routes
from patient_fao_agent.app.config import settings
import os

app = FastAPI(
    title="AI Patient Education & FAQ Agent",
    description="AI-powered patient education and medical query assistance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(education_routes.router, prefix="/api/v1", tags=["education"])
app.include_router(voice_routes.router, prefix="/api/v1", tags=["voice"])


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "chat.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy",
    "deepgram": "configured" if settings.DEEPGRAM_API_KEY else "missing",
    "elevenlabs": "configured" if settings.ELEVENLABS_API_KEY else "missing",
    "openai": "configured" if settings.OPENAI_API_KEY else "missing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)