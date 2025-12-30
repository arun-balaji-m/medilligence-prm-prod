# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from patient_referral_agent.app.routes.referral_routes import router as referral_router
# import os
#
# app = FastAPI(title="AI Referral & Coordination Agent")
#
# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Routes
# app.include_router(referral_router)
#
# # Static files
# static_path = os.path.join(os.path.dirname(__file__), "static")
# if os.path.exists("static"):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#
# @app.get("/")
# async def root():
#     return FileResponse(os.path.join(static_path, "chat.html"))
#
# @app.get("/health")
# async def health():
#     return {"status": "healthy"}
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

##second version

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from patient_referral_agent.app.routes.referral_routes import router as referral_router
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Referral & Coordination Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(referral_router)

# Static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "chat.html"))

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info("API available at: http://localhost:8000")
    logger.info("Health check: http://localhost:8000/health")
    logger.info("Test endpoint: http://localhost:8000/api/referral/test")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")