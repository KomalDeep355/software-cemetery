import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
# Load the .env that sits in the project root, no matter where the app is started from.
load_dotenv(ROOT / ".env")

CACHE_DIR = Path(os.getenv("CACHE_DIR", str(ROOT / "data" / "cache")))
try:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass  # read-only hosts: the client skips caching instead of crashing

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_TOKEN = TOKEN  # name used by github_client.py
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b").strip()
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "43200"))