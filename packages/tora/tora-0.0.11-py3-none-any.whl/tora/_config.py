import os

TORA_BASE_URL: str = os.getenv("TORA_BASE_URL", "https://api.toracker.com")
TORA_API_KEY: str | None = os.getenv("TORA_API_KEY", None)
