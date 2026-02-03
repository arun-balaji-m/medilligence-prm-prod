from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Initialize main gateway app
app = FastAPI(
    title="MediLligence AI Agents Gateway",
    description="Unified gateway for all medical AI agents",
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



from quick_business_engine.app.routes import router as quick_business_router

app.include_router(quick_business_router, prefix="/quick-business", tags=["quick-business"])


quick_business_static = os.path.join(os.path.dirname(__file__), "quick_business_engine", "app", "static")
if os.path.exists(quick_business_static):
    app.mount("/quick-business/static",StaticFiles(directory=quick_business_static), name="quick-business-static")

from fastapi.responses import FileResponse


@app.get("/quick-business")
@app.get("/quick-business/chat")
async def quick_business_chat():
    return FileResponse(os.path.join(quick_business_static, "chat.html"))


@app.get("/")
async def root():
    """Gateway landing page with all available agents"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MediLligence AI Agents Gateway</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 900px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 40px;
                font-size: 1.1em;
            }
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .agent-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-decoration: none;
                transition: transform 0.3s, box-shadow 0.3s;
                display: block;
            }
            .agent-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .agent-card h3 {
                margin-bottom: 10px;
                font-size: 1.3em;
            }
            .agent-card p {
                opacity: 0.9;
                font-size: 0.9em;
                line-height: 1.5;
            }
            .icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .health-status {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                text-align: center;
            }
            .status-badge {
                display: inline-block;
                padding: 5px 15px;
                background: #28a745;
                color: white;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MediLligence AI Agents</h1>
            <p class="subtitle">Unified Healthcare AI Agent Platform</p>

            <div class="agents-grid">
                <a href="/quick-business/chat" class="agent-card">
                    <div class="icon">📝</div>
                    <h3>Quick Business Engine</h3>
                    <p>All the non-technical users to interact with database using natural language</p>
                </a>
                
            </div>

            <div class="health-status">
                <span class="status-badge">● All Systems Operational</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check for all agents"""
    return {
        "status": "healthy",
        "gateway": "operational",
        "agents": {
            "quick-business": "mounted at /quick-business"
        }
    }


@app.get("/agents")
async def list_agents():
    """List all available agents and their endpoints"""
    return {
        "agents": [
            {
                "name": "Quick Business Agent",
                "path": "/quick-business",
                "description": "Ask questions about your data in plain English",
                "endpoints": ["/quick-business/", "/quick-business/health"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Starting MediLligence AI Agents Gateway")
    print("=" * 70)
    print("\nGateway URL: http://localhost:8000")
    print("\nAgent Routes:")
    print("  • Quick Business Agent:  http://localhost:8000/quick-business")
    print("\n" + "=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")