# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from appointment_agent.app.routes import appointment, ai_chat
# from appointment_agent.app.database import engine, Base
# import os
#
# # Create database tables
# Base.metadata.create_all(bind=engine)
#
# app = FastAPI(title="Appointment Agent API", version="1.0.0")
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(appointment.router)
# app.include_router(ai_chat.router)
#
# # Serve static files
# static_path = os.path.join(os.path.dirname(__file__), "..", "static")
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#
# @app.get("/")
# def read_root():
#     """Serve the chat interface"""
#     static_file = os.path.join(static_path, "chat.html")
#     if os.path.exists(static_file):
#         return FileResponse(static_file)
#     return {"message": "Appointment Agent API", "docs": "/docs"}
#
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from appointment_agent.app.routes import appointment, ai_chat
# from appointment_agent.app.database import engine, Base
# import os
#
# # Create database tables
# Base.metadata.create_all(bind=engine)
#
# app = FastAPI(title="Appointment Agent API", version="1.0.0")
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(appointment.router)
# app.include_router(ai_chat.router)
#
# # Serve static files - Fix the path resolution
# # Get absolute path to static directory
# current_dir = os.path.dirname(os.path.abspath(__file__))
# static_path = os.path.abspath(os.path.join(current_dir, "..", "static"))
#
# print(f"Current directory: {current_dir}")
# print(f"Static path: {static_path}")
# print(f"Static path exists: {os.path.exists(static_path)}")
#
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#     print(f"Static files mounted from: {static_path}")
# else:
#     print(f"Warning: Static directory not found at {static_path}")
#
#
# @app.get("/")
# def read_root():
#     """Serve the chat interface"""
#     chat_file = os.path.join(static_path, "chat.html")
#
#     # Debug logging
#     print(f"Looking for chat.html at: {chat_file}")
#     print(f"File exists: {os.path.exists(chat_file)}")
#
#     if os.path.exists(chat_file):
#         return FileResponse(chat_file)
#
#     # Return more helpful error message
#     return {
#         "message": "Appointment Agent API",
#         "docs": "/docs",
#         "error": "chat.html not found",
#         "expected_location": chat_file,
#         "static_path": static_path
#     }
#
#
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# #chat agent working model
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from appointment_agent.app.routes import appointment, ai_chat
# from appointment_agent.app.database import engine, Base
# import os
#
# # Create database tables
# Base.metadata.create_all(bind=engine)
#
# app = FastAPI(title="Appointment Agent API", version="1.0.0")
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(appointment.router)
# app.include_router(ai_chat.router)
#
# # Serve static files - static folder is in the same directory as main.py
# current_dir = os.path.dirname(os.path.abspath(__file__))
# static_path = os.path.join(current_dir, "static")
#
# print(f"Current directory: {current_dir}")
# print(f"Static path: {static_path}")
# print(f"Static path exists: {os.path.exists(static_path)}")
#
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#     print(f"Static files mounted from: {static_path}")
# else:
#     print(f"Warning: Static directory not found at {static_path}")
#
#
# @app.get("/")
# def read_root():
#     """Serve the chat interface"""
#     chat_file = os.path.join(static_path, "chat.html")
#
#     # Debug logging
#     print(f"Looking for chat.html at: {chat_file}")
#     print(f"File exists: {os.path.exists(chat_file)}")
#
#     if os.path.exists(chat_file):
#         return FileResponse(chat_file)
#
#     # Return more helpful error message
#     return {
#         "message": "Appointment Agent API",
#         "docs": "/docs",
#         "error": "chat.html not found",
#         "expected_location": chat_file,
#         "static_path": static_path
#     }
#
#
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# ##working version
#
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from appointment_agent.app.routes import appointment, ai_chat
# from appointment_agent.app.database import engine, Base
# import os
#
# # Create database tables
# Base.metadata.create_all(bind=engine)
#
# app = FastAPI(title="Appointment Agent API", version="1.0.0")
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(appointment.router)
# app.include_router(ai_chat.router)
# # Serve static files - static folder is in the same directory as main.py
# current_dir = os.path.dirname(os.path.abspath(__file__))
# static_path = os.path.join(current_dir, "static")
#
# print(f"Current directory: {current_dir}")
# print(f"Static path: {static_path}")
# print(f"Static path exists: {os.path.exists(static_path)}")
#
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#     print(f"Static files mounted from: {static_path}")
# else:
#     print(f"Warning: Static directory not found at {static_path}")
#
#
# @app.get("/")
# def read_root():
#     """Serve the chat interface"""
#     chat_file = os.path.join(static_path, "chat.html")
#
#     # Debug logging
#     print(f"Looking for chat.html at: {chat_file}")
#     print(f"File exists: {os.path.exists(chat_file)}")
#
#     if os.path.exists(chat_file):
#         return FileResponse(chat_file)
#
#     # Return more helpful error message
#     return {
#         "message": "Appointment Agent API",
#         "docs": "/docs",
#         "error": "chat.html not found",
#         "expected_location": chat_file,
#         "static_path": static_path
#     }
#
#
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# ##version one
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from appointment_agent.app.routes import appointment, ai_chat, voice_chat
# from appointment_agent.app.database import engine, Base
# import os
#
# # Create tables
# Base.metadata.create_all(bind=engine)
#
# app = FastAPI(
#     title="Medical Appointment Agent API",
#     description="AI-powered appointment booking system with voice capabilities",
#     version="1.0.0"
# )
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(appointment.router)
# app.include_router(ai_chat.router)
# app.include_router(voice_chat.router)
#
# current_dir = os.path.dirname(os.path.abspath(__file__))
# static_path = os.path.join(current_dir, "static")
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#     print(f"Static files mounted from: {static_path}")
# else:
#     print(f"Warning: Static directory not found at {static_path}")
#
# @app.get("/")
# async def root():
#     """Serve the chat interface"""
#     return FileResponse(os.path.join(static_path, "chat.html"))
#
# @app.get("/voice")
# async def voice_interface():
#     """Serve the voice interface"""
#     return FileResponse(os.path.join(static_path, "voice.html"))
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     import os
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if os.getenv("DEEPGRAM_API_KEY") else "missing",
#         "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing",
#         "anthropic": "configured" if os.getenv("ANTHROPIC_API_KEY") else "missing"
#     }
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from appointment_agent.app.routes import appointment, ai_chat, voice_chat
from appointment_agent.app.database import engine, Base
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Appointment Agent API",
    description="AI-powered appointment booking system with voice capabilities",
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

# Include routers
app.include_router(appointment.router)
app.include_router(ai_chat.router)
app.include_router(voice_chat.router)

# Serve static files
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    print(f"Static files mounted from: {static_path}")
else:
    print(f"Warning: Static directory not found at {static_path}")

@app.get("/")
async def root():
    """Serve the chat interface"""
    return FileResponse(os.path.join(static_path, "chat.html"))

@app.get("/voice")
async def voice_interface():
    """Serve the voice interface"""
    return FileResponse(os.path.join(static_path, "voice.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    return {
        "status": "healthy",
        "deepgram": "configured" if os.getenv("DEEPGRAM_API_KEY") else "missing",
        "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing",
        "openai": "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)