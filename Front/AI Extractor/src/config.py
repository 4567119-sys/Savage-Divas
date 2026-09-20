import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from module root
module_root = Path(__file__).parent.parent
load_dotenv(module_root / ".env")

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    ENABLE_LOCAL_FALLBACK: bool = os.getenv("ENABLE_LOCAL_FALLBACK", "true").lower() in ("true", "1", "yes")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

settings = Settings()
