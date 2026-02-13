"""Configuración del scraper."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SESSION_DIR = BASE_DIR / "session"
DATA_DIR = BASE_DIR / "data"

SESSION_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# URLs
APIRADAR_URL = "https://apiradar.live"
APIRADAR_LOGIN_URL = f"{APIRADAR_URL}/login"  # Ajustar si es diferente

# Configuración del navegador
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SESSION_FILE = SESSION_DIR / "apiradar_session.json"

# Tiempo de espera (segundos)
TIMEOUT = int(os.getenv("TIMEOUT", "30"))
