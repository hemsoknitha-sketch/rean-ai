import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Centralized configuration for Supreme Polymath AI Grandmaster Bot."""

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-3.6-flash").strip()

    MAX_MEMORY_TURNS: int = int(os.getenv("MAX_MEMORY_TURNS", "10"))
    ZERO_MARKDOWN_STRICT: bool = (
        os.getenv("ZERO_MARKDOWN_STRICT", "true").lower() == "true"
    )
    ENABLE_SEARCH_GROUNDING: bool = (
        os.getenv("ENABLE_SEARCH_GROUNDING", "true").lower() == "true"
    )
    ENABLE_CODE_EXECUTION: bool = (
        os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    )
    USE_LOCAL_MODEL: bool = (
        os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    )
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    LOCAL_MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "qwen2.5:7b-instruct").strip()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "859271875"))



    @classmethod
    def validate(cls) -> list[str]:
        """Validates critical credentials and returns a list of missing configuration items."""
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
            missing.append("TELEGRAM_BOT_TOKEN is missing or set to placeholder in .env")
        if not cls.GEMINI_API_KEY or "YourActualGeminiApiKey" in cls.GEMINI_API_KEY or cls.GEMINI_API_KEY == "your_gemini_api_key_here":
            missing.append("GEMINI_API_KEY is set to placeholder in .env. Replace it with your actual Google AI Studio key.")
        return missing

