import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROK_API_KEY = os.getenv("GROQ_API_KEY")

# Model Configuration
OPENAI_MODEL = "gpt-4o-mini"
GROK_MODEL = "llama-3.3-70b-versatile"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)