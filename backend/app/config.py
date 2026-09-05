import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend/ or project root
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "ShopWise AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Secret API key - Never send to frontend
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopwise.db")
    
    # ML Model directory
    MODEL_DIR: Path = Path(__file__).resolve().parent / "ml" / "assets"

settings = Settings()
