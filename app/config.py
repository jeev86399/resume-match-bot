import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    GROQ_API_KEY: str
    LLM_MODEL: str = "qwen/qwen3.8-27b"
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load environment variables: {e}")
    print("Please make sure you have created a .env file with TELEGRAM_BOT_TOKEN and GROQ_API_KEY")
    exit(1)
